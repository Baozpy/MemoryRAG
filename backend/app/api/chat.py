from fastapi import APIRouter
from pydantic import BaseModel
from app.core.state import embedder, vector_store
from app.core.llm import generate_answer

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/")
def chat(req: ChatRequest):
    query_embedding = embedder.encode([req.query])

    retrieved = vector_store.search(
        query_embedding,
        top_k=req.top_k
    )

    context = "\n\n".join(
        [r["text"] for r in retrieved]
    )

    answer = generate_answer(
        req.query,
        context
    )

    return {
        "query": req.query,
        "answer": answer,
        "retrieved": retrieved
    }