import hashlib
import numpy as np
from app.db import SessionLocal
from app.db_models import PromptCache
from app.services.embedding import get_embedding_service

def get_cached_prompt(prompt: str, mode: str):
    # 1. Exact Match Fast Path
    prompt_hash = hashlib.sha256(f"{mode}:{prompt}".encode()).hexdigest()
    with SessionLocal() as db:
        cached = db.query(PromptCache).filter(PromptCache.prompt_hash == prompt_hash).first()
        if cached:
            return {
                "optimized_prompt": cached.optimized_prompt,
                "tokens_before": cached.tokens_before,
                "tokens_after": cached.tokens_after
            }
            
        # 2. Semantic Match Path (Vector RAG Cache)
        embedder = get_embedding_service()
        query_vector = embedder.get_embedding(prompt)
        
        # Limit to recent 100 entries to maintain < 10ms search time
        recent_caches = db.query(PromptCache).filter(
            PromptCache.mode == mode,
            PromptCache.embedding_blob.is_not(None)
        ).order_by(PromptCache.id.desc()).limit(100).all()
        
        best_match = None
        highest_sim = 0.0
        
        for record in recent_caches:
            record_vector = np.frombuffer(record.embedding_blob, dtype=np.float32)
            sim = float(np.dot(query_vector, record_vector))
            if sim > highest_sim:
                highest_sim = sim
                best_match = record
                
        # 98% similarity threshold ensures the core intent and parameters are virtually identical
        if best_match and highest_sim > 0.98:
            return {
                "optimized_prompt": best_match.optimized_prompt,
                "tokens_before": best_match.tokens_before,
                "tokens_after": best_match.tokens_after
            }
            
        return None

def cache_prompt(prompt: str, mode: str, optimized_prompt: str, tokens_before: int, tokens_after: int):
    prompt_hash = hashlib.sha256(f"{mode}:{prompt}".encode()).hexdigest()
    
    embedder = get_embedding_service()
    embedding_vector = embedder.get_embedding(prompt)
    embedding_blob = embedding_vector.astype(np.float32).tobytes()
    
    with SessionLocal() as db:
        record = PromptCache(
            prompt_hash=prompt_hash,
            mode=mode,
            optimized_prompt=optimized_prompt,
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            embedding_blob=embedding_blob
        )
        db.add(record)
        try:
            db.commit()
        except Exception:
            db.rollback()
