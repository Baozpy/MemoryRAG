import time
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.state import embedder, vector_store

router = APIRouter()


class UploadTextRequest(BaseModel):
    text: str
    source: str = "user_input"


def chunk_text(text: str, chunk_size: int = 500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks


@router.post("/upload_text")
def upload_text(req: UploadTextRequest):
    chunks = chunk_text(req.text)
    embeddings = embedder.encode(chunks)

    metadata = [
    {
        "source": req.source,
        "created_at": time.time(),
        "last_access_time": time.time(),
        "type": "document",
        "importance": 0.8,
        "retrieval_count": 0,
        "memory_score": 0.8,
        "is_active": True,
    }
    for _ in chunks
]

    vector_store.add(embeddings, chunks, metadata)

    return {
        "message": "uploaded",
        "chunks": len(chunks)
    }