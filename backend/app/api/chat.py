from fastapi import APIRouter
from pydantic import BaseModel
from app.core.state import embedder, vector_store
from app.core.llm import generate_answer
from app.memory.memory_agent import MemoryAgent

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

    agent_memory_saved = False

    if MemoryAgent.should_save_memory(req.query, answer):
        memory = MemoryAgent.build_memory(
            req.query,
            answer
        )

        memory_embedding = embedder.encode(
            [memory["text"]]
        )

        vector_store.add(
            memory_embedding,
            [memory["text"]],
            [memory["metadata"]]
        )

        agent_memory_saved = True

    return {
        "query": req.query,
        "answer": answer,
        "retrieved": retrieved,
        "agent_memory_saved": agent_memory_saved
    }