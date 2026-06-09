import math
import time


def recency_score(
    last_access_time: float,
    lambda_decay: float = 0.01
):
    age = time.time() - last_access_time

    return math.exp(
        -lambda_decay * age
    )


def frequency_score(
    retrieval_count: int
):
    return 1 + math.log1p(
        retrieval_count
    )


def compute_memory_score(
    importance: float,
    retrieval_count: int,
    last_access_time: float
):
    return (
        importance
        * recency_score(last_access_time)
        * frequency_score(retrieval_count)
    )