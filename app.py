from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv

from database.metrics import get_metrics
from database.postgres_sql import create_database
from database.create_table import create_tables
from vectorstore.create_index import create_index
from routes.ingestion import router as ingestion_router
from routes.chat import router as chat_router, chat_websocket_handler

load_dotenv()

app = FastAPI(
    title="AI-Powered Investor Intelligence Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/chat")
async def websocket_root_chat(websocket: WebSocket):
    await chat_websocket_handler(websocket)


@app.on_event("startup")
def startup_event():
    """
    Initialize database and vector index on app startup.
    """
    create_database()
    create_tables()
    
    azure_search_ep = os.getenv("AZURE_SEARCH_ENDPOINT")
    azure_search_key = os.getenv("AZURE_SEARCH_API_KEY")
    azure_search_index = os.getenv("AZURE_SEARCH_INDEX_NAME")
    if azure_search_ep and azure_search_key and azure_search_index:
        try:
            create_index(
                endpoint=azure_search_ep,
                api_key=azure_search_key,
                index_name=azure_search_index
            )
        except Exception as e:
            print(f"Warning: Could not create vector index: {e}")
    else:
        print("Note: Azure Search credentials not provided in .env. Running in local storage mode.")

app.include_router(
    ingestion_router,
    prefix="/api",
    tags=["Ingestion"]
)

app.include_router(
    chat_router,
    prefix="/api",
    tags=["Chat"]
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)


@app.get("/")
def dashboard(request: Request):
    """
    Render dashboard UI.
    """
    metrics = get_metrics()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "metrics": metrics,
            "total_companies": len(metrics),
            "total_reports": len(metrics)
        }
    )


@app.get("/api/metrics")
def metrics():
    """
    Return KPI metrics.
    """
    return JSONResponse(
        content=get_metrics()
    )


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )