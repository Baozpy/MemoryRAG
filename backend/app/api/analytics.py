from fastapi import APIRouter
from app.core.state import vector_store

router = APIRouter()


@router.get("/")
def get_analytics():
    memories = []

    for text, meta in zip(
        vector_store.texts,
        vector_store.metadata
    ):
        memories.append({
            "text": text,
            "source": meta.get("source"),
            "type": meta.get("type"),
            "importance": meta.get("importance", 0),
            "retrieval_count": meta.get("retrieval_count", 0),
            "memory_score": meta.get("memory_score", 0),
            "created_at": meta.get("created_at"),
            "last_access_time": meta.get("last_access_time")
        })

    memory_count = len(memories)

    if memory_count == 0:
        return {
            "memory_count": 0,
            "avg_memory_score": 0,
            "avg_retrieval_count": 0,
            "top_memories": []
        }

    avg_memory_score = sum(
        m["memory_score"] for m in memories
    ) / memory_count

    avg_retrieval_count = sum(
        m["retrieval_count"] for m in memories
    ) / memory_count

    top_memories = sorted(
        memories,
        key=lambda x: x["memory_score"],
        reverse=True
    )[:5]

    return {
        "memory_count": memory_count,
        "avg_memory_score": avg_memory_score,
        "avg_retrieval_count": avg_retrieval_count,
        "top_memories": top_memories
    }

@router.get("/history")
def memory_history():

    return {
        "history": vector_store.get_history()
    }