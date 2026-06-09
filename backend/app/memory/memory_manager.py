from app.memory.memory_decay import (
    compute_memory_score
)

import time


class MemoryManager:

    @staticmethod
    def refresh_memory(memory):

        memory["memory_score"] = (
            compute_memory_score(
                importance=memory["importance"],
                retrieval_count=memory["retrieval_count"],
                last_access_time=memory["last_access_time"]
            )
        )

        return memory