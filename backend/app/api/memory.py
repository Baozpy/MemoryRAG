from fastapi import APIRouter
from app.core.state import vector_store

router = APIRouter()


@router.get("/")
def list_memory():
    return {
        "total_items": len(vector_store.texts),
        "items": [
            {
                "text": text,
                "metadata": meta
            }
            for text, meta in zip(vector_store.texts, vector_store.metadata)
        ]
    }