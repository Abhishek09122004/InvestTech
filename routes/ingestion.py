import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
import os

from ingestion.extract_metrics import extract_metrics_from_pdf

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    upload_dir = Path("data/raw_pdfs")
    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = upload_dir / file.filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        print(f"[Upload] File saved to {file_path}. Processing and extracting metrics...")

        # 1. High-accuracy financial KPI extraction and database persistence
        extraction_result = extract_metrics_from_pdf(str(file_path))

        # 2. Vector store indexing if Azure credentials are configured
        if os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_SEARCH_ENDPOINT"):
            try:
                from langchain_openai import AzureOpenAIEmbeddings
                from vectorstore.azure_ai_search import AzureAISearchVectorStore
                from ingestion.ingest_documents import ingest_document

                embeddings = AzureOpenAIEmbeddings(
                    model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
                )

                vector_store = AzureAISearchVectorStore(
                    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
                    api_key=os.getenv("AZURE_SEARCH_API_KEY"),
                    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
                )

                ingest_document(
                    pdf_path=str(file_path),
                    embeddings=embeddings,
                    vector_store=vector_store
                )
            except Exception as e:
                print(f"Warning during vector ingestion: {e}")
        else:
            print(f"[Upload] Azure Search credentials not configured. Local database and markdown persistence complete.")

        return {
            "status": "success",
            "message": f"Document '{file.filename}' processed and stored successfully.",
            "file_name": file.filename,
            "company": extraction_result.get("company", ""),
            "year": extraction_result.get("year", ""),
            "metrics": extraction_result.get("metrics", {})
        }

    except Exception as exc:
        print(f"[Upload Error] {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process and store document: {str(exc)}"
        )