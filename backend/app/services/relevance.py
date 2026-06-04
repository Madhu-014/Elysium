import re
import numpy as np
from app.services.embedding import get_embedding_service

COURTESY_PREFIXES = (
    "hello",
    "thank you",
    "i really appreciate",
    "i am looking forward",
)

LIST_ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+")

def _sentence_split(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [c.strip() for c in chunks if c.strip()]

def _is_hard_requirement(sentence: str) -> bool:
    s = sentence.lower()
    if LIST_ITEM_RE.match(sentence):
        return True
    return any(
        marker in s
        for marker in (
            "focus on", "provide", "do not", "must", "to recap", "make sure", "keep the", "professional"
        )
    )

def _is_courtesy_line(line: str) -> bool:
    normalized = line.strip().lower()
    return any(normalized.startswith(prefix) for prefix in COURTESY_PREFIXES)

def filter_relevant_sentences(text: str, mode: str) -> str:
    stripped = text.strip()
    if not stripped:
        return stripped

    sentences = _sentence_split(stripped)
    if len(sentences) <= 2:
        return stripped

    embedder = get_embedding_service()
    
    # Encode the full text to capture the global intent
    core_intent_vector = embedder.get_embedding(stripped)
    
    scored: list[tuple[float, int, str]] = []
    
    for idx, sentence in enumerate(sentences):
        if _is_courtesy_line(sentence):
            # Heavily penalize courtesy fluff so it gets dropped
            scored.append((-1.0, idx, sentence))
            continue
            
        vector = embedder.get_embedding(sentence)
        similarity = float(np.dot(core_intent_vector, vector))
        
        # Boost score if it contains hard constraints
        if _is_hard_requirement(sentence):
            similarity += 0.25
            
        scored.append((similarity, idx, sentence))

    # Keep ratio based on mode
    keep_ratio = {"eco-max": 0.25, "optimal": 0.50, "precision": 0.9}[mode]
    min_keep = {"eco-max": 1, "optimal": 2, "precision": 4}[mode]
    keep_count = min(len(sentences), max(int(len(sentences) * keep_ratio), min_keep))

    top_scored = sorted(scored, key=lambda item: (item[0], -item[1]), reverse=True)[:keep_count]
    keep_indices = {idx for _score, idx, _sentence in top_scored}

    # Always keep the opening sentence for base context
    keep_indices.add(0)
    
    # Always keep explicit requirements regardless of quota
    for idx, sentence in enumerate(sentences):
        if _is_hard_requirement(sentence):
            keep_indices.add(idx)

    kept = [sentence for idx, sentence in enumerate(sentences) if idx in keep_indices]
    return "\n".join(kept)
