from fastapi import FastAPI
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.memory import router as memory_router
from app.api.analytics import router as analytics_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MemoryRAG")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router, prefix="/documents", tags=["documents"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(memory_router, prefix="/memory", tags=["memory"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

@app.get("/health")
def health():
    return {"status": "ok", "project": "MemoryRAG"}