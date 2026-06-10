from fastapi import APIRouter, Query
from app.core.state import vector_store
from app.services.agent_memory import (
    add_agent_memory,
    retention_score,
    get_forget_candidates,
    forget_low_score,
    consolidate_memories,
    update_memory_access,
    memory_stats
)

router = APIRouter()

# @router.get("/")
# def list_memory():
#     return {
#         "total_items": len(vector_store.texts),
#         "items": [
#             {
#                 "text": text,
#                 "metadata": meta
#             }
#             for text, meta in zip(vector_store.texts, vector_store.metadata)
#         ]
#     }

@router.get("/")
def list_memory():
    return {
        "total_items": len(vector_store.texts),
        "items": [
            {
                "index": index,
                "text": text,
                "metadata": metadata,
                "retention_score": retention_score(metadata)
            }
            for index, (text, metadata) in enumerate(
                zip(vector_store.texts, vector_store.metadata)
            )
        ]
    }


@router.get("/forget_candidates")
def forget_candidates(threshold: float = 1.0):
    candidates = []

    for text, meta in zip(
        vector_store.texts,
        vector_store.metadata
    ):
        if (
            meta.get("memory_score", 0) < threshold
            and meta.get("is_active", True)
        ):
            candidates.append({
                "text": text,
                "memory_score": meta.get("memory_score", 0),
                "retrieval_count": meta.get("retrieval_count", 0),
                "threshold": threshold
            })

    return {
        "threshold": threshold,
        "count": len(candidates),
        "candidates": candidates
    }


@router.post("/forget_low_score")
def forget_low_score(threshold: float = 1.0):
    forgotten = 0

    for meta in vector_store.metadata:
        if (
            meta.get("memory_score", 0) < threshold
            and meta.get("is_active", True)
        ):
            meta["is_active"] = False
            forgotten += 1

    return {
        "forgotten": forgotten,
        "threshold": threshold
    }








@router.post("/agent")
def create_agent_memory(text: str):
    return add_agent_memory(text)


@router.post("/reflect")
def reflect_memory():
    return consolidate_memories()


@router.post("/access/{index}")
def access_memory(index: int):
    return update_memory_access(index)


@router.get("/stats")
def get_memory_stats():
    return memory_stats()