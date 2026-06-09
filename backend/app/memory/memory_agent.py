import time


class MemoryAgent:
    @staticmethod
    def should_save_memory(query: str, answer: str) -> bool:
        save_keywords = [
            "i like",
            "i prefer",
            "my project",
            "i am building",
            "i study",
            "i work on",
            "remember",
            "important"
        ]

        text = f"{query} {answer}".lower()

        return any(keyword in text for keyword in save_keywords)

    @staticmethod
    def build_memory(query: str, answer: str):
        return {
            "text": f"User asked: {query}\nAssistant answered: {answer}",
            "metadata": {
                "source": "agent_auto_memory",
                "created_at": time.time(),
                "last_access_time": time.time(),
                "type": "conversation",
                "importance": 0.7,
                "retrieval_count": 0,
                "memory_score": 1.0,
                "is_active": True
            }
        }