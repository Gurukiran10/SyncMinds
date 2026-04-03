"""
Semantic search and knowledge base service.
Uses sentence-transformers for local embeddings stored as JSON in PostgreSQL.
"""
import json
import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.meeting import Meeting
from app.models.user import User

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    """Lazy-load the sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loaded sentence-transformers model: all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence-transformers not installed — semantic search unavailable")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
    return _model


def embed_text(text: str) -> Optional[List[float]]:
    """Embed a text string into a float vector."""
    model = _get_model()
    if not model:
        return None
    try:
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return None


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def index_meeting(db: Session, meeting: Meeting, transcript_text: str) -> bool:
    """
    Store semantic embeddings for a meeting.
    Chunks: executive summary, discussion topics, and transcript excerpt.
    Embeddings are stored in meeting_metadata under 'embeddings'.
    """
    chunks = []

    if meeting.summary:
        chunks.append({"type": "summary", "text": str(meeting.summary)})

    topics = meeting.discussion_topics or []
    if topics:
        chunks.append({"type": "topics", "text": " ".join(str(t) for t in topics)})

    if transcript_text:
        # Store first 2000 chars of transcript as a searchable chunk
        chunks.append({"type": "transcript", "text": transcript_text[:2000]})

    embeddings = []
    for chunk in chunks:
        vector = embed_text(chunk["text"])
        if vector:
            embeddings.append({
                "type": chunk["type"],
                "text": chunk["text"][:500],
                "vector": vector,
                "indexed_at": datetime.utcnow().isoformat(),
            })

    if not embeddings:
        return False

    metadata = dict(meeting.meeting_metadata or {})
    metadata["embeddings"] = embeddings
    meeting.meeting_metadata = metadata  # type: ignore[assignment]
    db.commit()
    logger.info(f"Indexed {len(embeddings)} chunks for meeting {meeting.id}")
    return True


def semantic_search(
    query: str,
    db: Session,
    user: User,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Search meetings semantically using cosine similarity.
    Returns ranked list of matching meeting snippets.
    """
    query_vector = embed_text(query)
    if not query_vector:
        # Fallback: keyword search on title/summary
        return _keyword_search(query, db, user, limit)

    user_id = str(user.id)
    all_meetings = db.execute(select(Meeting)).scalars().all()

    results = []
    for meeting in all_meetings:
        # Access control
        attendee_ids = [str(aid) for aid in (meeting.attendee_ids or [])]
        if str(meeting.organizer_id) != user_id and user_id not in attendee_ids:
            continue

        metadata = meeting.meeting_metadata or {}
        embeddings = metadata.get("embeddings", [])

        best_score = 0.0
        best_chunk = None
        for emb in embeddings:
            vector = emb.get("vector")
            if not vector:
                continue
            score = _cosine_similarity(query_vector, vector)
            if score > best_score:
                best_score = score
                best_chunk = emb

        if best_score > 0.3 and best_chunk:
            results.append({
                "meeting_id": str(meeting.id),
                "meeting_title": meeting.title,
                "meeting_date": meeting.scheduled_start.isoformat() if meeting.scheduled_start else None,
                "chunk_type": best_chunk.get("type"),
                "snippet": best_chunk.get("text", "")[:300],
                "score": round(best_score, 4),
            })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]


def _keyword_search(query: str, db: Session, user: User, limit: int) -> List[Dict[str, Any]]:
    """Fallback keyword search on title and summary."""
    user_id = str(user.id)
    q = query.lower()
    all_meetings = db.execute(select(Meeting)).scalars().all()

    results = []
    for meeting in all_meetings:
        attendee_ids = [str(aid) for aid in (meeting.attendee_ids or [])]
        if str(meeting.organizer_id) != user_id and user_id not in attendee_ids:
            continue

        title = str(meeting.title or "").lower()
        summary = str(meeting.summary or "").lower()
        if q in title or q in summary:
            results.append({
                "meeting_id": str(meeting.id),
                "meeting_title": meeting.title,
                "meeting_date": meeting.scheduled_start.isoformat() if meeting.scheduled_start else None,
                "chunk_type": "keyword",
                "snippet": (meeting.summary or meeting.title or "")[:300],
                "score": 1.0 if q in title else 0.5,
            })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]


def get_recurring_topics(db: Session, user: User, min_count: int = 2) -> List[Dict[str, Any]]:
    """Return topics that appear across multiple meetings."""
    user_id = str(user.id)
    all_meetings = db.execute(select(Meeting)).scalars().all()

    topic_counts: Dict[str, List[str]] = {}
    for meeting in all_meetings:
        attendee_ids = [str(aid) for aid in (meeting.attendee_ids or [])]
        if str(meeting.organizer_id) != user_id and user_id not in attendee_ids:
            continue

        for topic in (meeting.discussion_topics or []):
            t = str(topic).lower().strip()
            if t:
                topic_counts.setdefault(t, []).append(str(meeting.id))

    return [
        {"topic": topic, "meeting_count": len(mids), "meeting_ids": mids}
        for topic, mids in topic_counts.items()
        if len(mids) >= min_count
    ]
