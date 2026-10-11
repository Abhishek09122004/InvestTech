import asyncio
import json
import os
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from rag.local_analyst import analyze_financial_query, stream_financial_query

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    company: str | None = None
    year: int | None = None


async def get_chat_stream_generator(
    question: str,
    company: str | None = None,
    year: int | None = None
) -> AsyncGenerator[str, None]:
    """
    Unified streaming generator that streams response chunks either from
    Azure OpenAI (if configured) or the local real-time analyst engine.
    """
    if os.getenv("AZURE_SEARCH_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY"):
        try:
            from vectorstore.azure_ai_search import AzureAISearchVectorStore, Retriever
            from llm.azure_openai import get_openai_client

            vector_store = AzureAISearchVectorStore(
                endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
                api_key=os.getenv("AZURE_SEARCH_API_KEY"),
                index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
            )
            retriever = Retriever(vector_store.client)

            if company and year:
                docs = retriever.invoke(query=question, company=company, year=year)
            else:
                docs = retriever.invoke(query=question)
            context = "\n\n".join(doc.page_content for doc in docs)

            prompt = (
                "You are an expert financial analyst. Use the following context from corporate reports "
                "to answer the user's question clearly with formatted markdown tables and bullet points. "
                "If the context does not contain relevant information, politely indicate that you need more data.\n\n"
                f"Context:\n{context}\n\n"
                f"User Question: {question}\n\nAnswer:"
            )

            client = get_openai_client()
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o"),
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return
        except Exception as e:
            # Fall back to local stream on Azure error
            yield f"\n*(Notice: Azure stream fallback: {e})*\n\n"

    # Local real-time streaming analyst engine
    async for chunk in stream_financial_query(question, company, year):
        yield chunk


async def chat_websocket_handler(websocket: WebSocket):
    """
    Bidirectional real-time WebSocket handler for chat.
    Supports real-time streaming, status events, and stop-generation signals.
    """
    await websocket.accept()
    current_stream_task: asyncio.Task | None = None

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                msg = json.loads(raw_data)
            except Exception:
                continue

            msg_type = msg.get("type", "chat")

            # Heartbeat ping
            if msg_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue

            # Stop generation signal
            if msg_type == "stop":
                if current_stream_task and not current_stream_task.done():
                    current_stream_task.cancel()
                    current_stream_task = None
                await websocket.send_text(json.dumps({"type": "stopped"}))
                continue

            # Chat prompt
            question = msg.get("question", "").strip()
            if not question:
                continue

            company = msg.get("company")
            year = msg.get("year")

            # Notify client that analyst is searching / preparing
            company_str = f" for {company}" if company else ""
            await websocket.send_text(json.dumps({
                "type": "status",
                "message": f"Analyzing 10-K filings and financial metrics{company_str}..."
            }))

            # Stream generation runner
            async def run_stream(q, c, y):
                full_text_acc = []
                try:
                    async for chunk in get_chat_stream_generator(q, c, y):
                        full_text_acc.append(chunk)
                        await websocket.send_text(json.dumps({
                            "type": "chunk",
                            "text": chunk
                        }))
                    await websocket.send_text(json.dumps({
                        "type": "done",
                        "full_text": "".join(full_text_acc)
                    }))
                except asyncio.CancelledError:
                    await websocket.send_text(json.dumps({
                        "type": "stopped",
                        "full_text": "".join(full_text_acc)
                    }))
                except Exception as err:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(err)
                    }))

            if current_stream_task and not current_stream_task.done():
                current_stream_task.cancel()

            current_stream_task = asyncio.create_task(run_stream(question, company, year))

    except WebSocketDisconnect:
        if current_stream_task and not current_stream_task.done():
            current_stream_task.cancel()
    except Exception:
        if current_stream_task and not current_stream_task.done():
            current_stream_task.cancel()


@router.websocket("/ws/chat")
async def ws_chat_endpoint(websocket: WebSocket):
    await chat_websocket_handler(websocket)


@router.post("/chat/stream")
async def chat_sse_stream(request: ChatRequest):
    """
    Server-Sent Events (SSE) streaming endpoint.
    Yields event stream chunks for clients that prefer fetch stream over WebSocket.
    """
    async def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'status', 'message': 'Retrieving 10-K filings...'})}\n\n"
            async for chunk in get_chat_stream_generator(request.question, request.company, request.year):
                yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Non-streaming fallback endpoint for backward compatibility.
    """
    try:
        if not os.getenv("AZURE_SEARCH_ENDPOINT") or not os.getenv("AZURE_OPENAI_API_KEY"):
            answer = analyze_financial_query(
                question=request.question,
                selected_company=request.company,
                year=request.year
            )
            return {"answer": answer}

        from vectorstore.azure_ai_search import AzureAISearchVectorStore, Retriever
        from llm.azure_openai import get_openai_client

        vector_store = AzureAISearchVectorStore(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            api_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
        )
        retriever = Retriever(vector_store.client)

        if request.company and request.year:
            docs = retriever.invoke(
                query=request.question,
                company=request.company,
                year=request.year
            )
        else:
            docs = retriever.invoke(query=request.question)
        context = "\n\n".join(doc.page_content for doc in docs)

        prompt = (
            "You are an expert financial analyst. Use the following context from corporate reports to answer "
            "the user's question clearly. If the context does not contain relevant information, politely indicate that.\n\n"
            f"Context:\n{context}\n\nUser Question: {request.question}\n\nAnswer:"
        )

        client = get_openai_client()
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
