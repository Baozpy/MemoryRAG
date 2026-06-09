import time
from typing import Literal
from pydantic import BaseModel, Field


class MemoryMetadata(BaseModel):
    source: str = "user_input"
    type: Literal["document", "conversation"] = "document"
    created_at: float = Field(default_factory=time.time)
    importance: float = 0.8
    retrieval_count: int = 0
    memory_score: float = 0.8
    