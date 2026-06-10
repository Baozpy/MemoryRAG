from datetime import datetime, timezone
from typing import Dict, Any, List
import json
import re

from app.core.state import vector_store

try:
    from app.core.state import llm
except ImportError:
    llm = None


VALID_MEMORY_TYPES = {
    "semantic",
    "episodic",
    "preference",
    "task",
    "reflection"
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_json_parse(raw_text: str) -> Dict[str, Any]:
    try:
        return json.loads(raw_text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)

    if not match:
        return {}

    try:
        return json.loads(match.group(0))
    except Exception:
        return {}


def call_llm(prompt: str) -> str:
    if llm is None:
        return ""

    try:
        if hasattr(llm, "invoke"):
            response = llm.invoke(prompt)

            if hasattr(response, "content"):
                return response.content

            return str(response)

        if callable(llm):
            return str(llm(prompt))

    except Exception:
        return ""

    return ""


def analyze_memory(text: str) -> Dict[str, Any]:
    prompt = f"""
You are a memory management module for an AI agent.

Analyze the following user memory and return a JSON object only.

Memory types:
- semantic: stable facts about the user, background, identity, long-term knowledge
- episodic: specific events, experiences, or time-based memories
- preference: user preferences, communication style, likes, dislikes
- task: goals, deadlines, applications, interviews, projects, or action items

Importance scale:
1 = trivial or short-lived
2 = mildly useful
3 = useful context
4 = important long-term context
5 = critical long-term memory

Return format:
{{
  "type": "semantic | episodic | preference | task",
  "importance": 1,
  "reason": "brief explanation"
}}

Memory:
{text}
"""

    raw_response = call_llm(prompt)
    parsed = safe_json_parse(raw_response)

    memory_type = parsed.get("type", "semantic")
    importance = parsed.get("importance", 2)
    reason = parsed.get("reason", "Default fallback classification.")

    if memory_type not in VALID_MEMORY_TYPES:
        memory_type = "semantic"

    try:
        importance = int(importance)
    except Exception:
        importance = 2

    importance = max(1, min(importance, 5))

    return {
        "type": memory_type,
        "importance": importance,
        "reason": reason
    }


def add_agent_memory(text: str) -> Dict[str, Any]:
    analysis = analyze_memory(text)

    metadata = {
        "type": analysis["type"],
        "importance": analysis["importance"],
        "classification_reason": analysis["reason"],
        "created_at": utc_now(),
        "last_accessed": utc_now(),
        "access_count": 0,
        "status": "active",
        "source": "agent_memory"
    }

    vector_store.add_text(text, metadata)

    return {
        "text": text,
        "metadata": metadata
    }


def calculate_recency_score(metadata: Dict[str, Any]) -> float:
    created_at = metadata.get("created_at")

    if not created_at:
        return 1.0

    try:
        created_time = datetime.fromisoformat(created_at)
        current_time = datetime.now(timezone.utc)

        if created_time.tzinfo is None:
            created_time = created_time.replace(tzinfo=timezone.utc)

        age_days = (current_time - created_time).days

        if age_days <= 1:
            return 1.0
        if age_days <= 7:
            return 0.8
        if age_days <= 30:
            return 0.5
        if age_days <= 90:
            return 0.3

        return 0.1

    except Exception:
        return 1.0


def retention_score(metadata: Dict[str, Any]) -> float:
    importance = float(metadata.get("importance", 1))
    access_count = float(metadata.get("access_count", 0))
    recency = calculate_recency_score(metadata)

    normalized_access = min(access_count / 5.0, 1.0)

    score = (
        importance * 0.5
        + normalized_access * 2.0 * 0.3
        + recency * 2.0 * 0.2
    )

    return round(score, 3)


def build_forgetting_reason(
    metadata: Dict[str, Any],
    score: float,
    threshold: float
) -> str:
    reasons = []

    if metadata.get("importance", 1) <= 1:
        reasons.append("low importance")

    if metadata.get("access_count", 0) == 0:
        reasons.append("never accessed")

    if calculate_recency_score(metadata) <= 0.3:
        reasons.append("old memory")

    if not reasons:
        reasons.append("low retention score")

    return f"{', '.join(reasons)}; score={score}, threshold={threshold}"


def get_forget_candidates(threshold: float = 1.0) -> List[Dict[str, Any]]:
    candidates = []

    for index, (text, metadata) in enumerate(
        zip(vector_store.texts, vector_store.metadata)
    ):
        if metadata.get("status") == "forgotten":
            continue

        score = retention_score(metadata)

        if score < threshold:
            candidates.append({
                "index": index,
                "text": text,
                "metadata": metadata,
                "retention_score": score,
                "reason": build_forgetting_reason(metadata, score, threshold)
            })

    return candidates


def forget_low_score(threshold: float = 1.0) -> Dict[str, Any]:
    kept_texts = []
    kept_metadata = []
    forgotten_items = []

    for text, metadata in zip(vector_store.texts, vector_store.metadata):
        score = retention_score(metadata)

        if score < threshold:
            forgotten_items.append({
                "text": text,
                "metadata": metadata,
                "retention_score": score
            })
        else:
            kept_texts.append(text)
            kept_metadata.append(metadata)

    vector_store.texts = kept_texts
    vector_store.metadata = kept_metadata

    if hasattr(vector_store, "embeddings"):
        vector_store.embeddings = vector_store.embeddings[:len(kept_texts)]

    return {
        "deleted_count": len(forgotten_items),
        "remaining_count": len(vector_store.texts),
        "deleted_items": forgotten_items
    }


def update_memory_access(index: int) -> Dict[str, Any]:
    if index < 0 or index >= len(vector_store.metadata):
        return {
            "error": "Invalid memory index"
        }

    metadata = vector_store.metadata[index]
    metadata["access_count"] = metadata.get("access_count", 0) + 1
    metadata["last_accessed"] = utc_now()

    vector_store.metadata[index] = metadata

    return {
        "index": index,
        "metadata": metadata
    }


def build_reflection_summary(memory_type: str, items: List[str]) -> str:
    selected_items = items[:5]
    joined_items = "\n".join(f"- {item}" for item in selected_items)

    prompt = f"""
You are a memory reflection module for an AI agent.

Create a concise high-level reflection from the following memories.

Memory type:
{memory_type}

Memories:
{joined_items}

Return only one sentence.
"""

    response = call_llm(prompt).strip()

    if response:
        return response

    return (
        f"The user has multiple {memory_type} memories related to: "
        f"{'; '.join(selected_items[:3])}"
    )


def consolidate_memories() -> Dict[str, Any]:
    grouped = {}

    for text, metadata in zip(vector_store.texts, vector_store.metadata):
        memory_type = metadata.get("type", "semantic")
        status = metadata.get("status", "active")

        if status == "forgotten":
            continue

        if memory_type == "reflection":
            continue

        grouped.setdefault(memory_type, []).append(text)

    created_reflections = []

    for memory_type, items in grouped.items():
        if len(items) < 3:
            continue

        summary = build_reflection_summary(memory_type, items)

        reflection_metadata = {
            "type": "reflection",
            "importance": 4,
            "classification_reason": "Generated from memory consolidation.",
            "created_at": utc_now(),
            "last_accessed": utc_now(),
            "access_count": 0,
            "status": "active",
            "source": "reflection",
            "reflection_from": memory_type
        }

        vector_store.add_text(summary, reflection_metadata)

        created_reflections.append({
            "text": summary,
            "metadata": reflection_metadata
        })

    return {
        "created_count": len(created_reflections),
        "created_reflections": created_reflections
    }


def memory_stats() -> Dict[str, Any]:
    type_counts = {}
    total_score = 0.0

    for metadata in vector_store.metadata:
        memory_type = metadata.get("type", "unknown")
        type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
        total_score += retention_score(metadata)

    total_items = len(vector_store.metadata)

    average_retention_score = (
        round(total_score / total_items, 3)
        if total_items > 0
        else 0
    )

    return {
        "total_items": total_items,
        "type_counts": type_counts,
        "average_retention_score": average_retention_score
    }