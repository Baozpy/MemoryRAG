import time
import faiss
import numpy as np
from typing import List, Dict, Any
from app.memory.memory_decay import compute_memory_score


class VectorStore:
    def __init__(self, dim: int = 1024):
        self.index = faiss.IndexFlatIP(dim)
        self.texts: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.memory_history: List[Dict[str, Any]] = []

    def add(
        self,
        embeddings: np.ndarray,
        texts: List[str],
        metadata: List[Dict[str, Any]]
    ):
        self.index.add(embeddings)
        self.texts.extend(texts)
        self.metadata.extend(metadata)

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        if self.index.ntotal == 0:
            return []

        scores, indices = self.index.search(query_embedding, top_k)

        results = []

        for semantic_score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            meta = self.metadata[idx]
            if not meta.get("is_active", True):
                continue

            meta["retrieval_count"] = meta.get("retrieval_count", 0) + 1

            meta["memory_score"] = compute_memory_score(
                importance=meta.get("importance", 0.5),
                retrieval_count=meta.get("retrieval_count", 0),
                last_access_time=meta.get("last_access_time", time.time())
            )

            self.memory_history.append({
                "time": time.time(),
                "text": self.texts[idx][:100],
                "memory_score": meta["memory_score"],
                "retrieval_count": meta["retrieval_count"]
            })

            meta["last_access_time"] = time.time()

            combined_score = float(semantic_score) * meta["memory_score"]

            results.append({
                "text": self.texts[idx],
                "semantic_score": float(semantic_score),
                "memory_score": meta["memory_score"],
                "combined_score": combined_score,
                "metadata": meta
            })

        results = sorted(
            results,
            key=lambda x: x["combined_score"],
            reverse=True
        )

        return results
    
    def get_history(self):
        return self.memory_history