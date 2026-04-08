"""
Embedder Module using Local Sentence-Transformers (Offline Mode)
No network requests – uses cached model only.
"""

import os
import numpy as np
import asyncio
from sentence_transformers import SentenceTransformer

from app.config import config
from app.utils.logger import logger

# Force offline mode before importing model
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

class Embedder:
    """
    Create embeddings using local sentence-transformers model
    Loads model once and reuses it (no network calls)
    """
    
    _model = None  # Class-level cache to avoid reloading in subprocesses
    
    def __init__(self):
        self.model_name = config.EMBEDDING_MODEL
        self.dimension = config.EMBEDDING_DIM
        
        # Use cached model if already loaded
        if Embedder._model is None:
            logger.info(f"Loading embedding model: {self.model_name} (offline mode)")
            try:
                # Load from local cache only
                Embedder._model = SentenceTransformer(
                    self.model_name,
                    cache_folder=os.path.expanduser("~/.cache/huggingface/hub")
                )
                self.dimension = Embedder._model.get_sentence_embedding_dimension()
                logger.info(f"Embedder initialized with dimension {self.dimension}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                logger.error("Make sure the model is cached. Run: python -c \"from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')\"")
                raise
        else:
            logger.info(f"Using cached embedding model")
            self.dimension = Embedder._model.get_sentence_embedding_dimension()
        
        self.model = Embedder._model
    
    async def embed(self, text: str, use_cache: bool = True) -> np.ndarray:
        """Create embedding for single text"""
        loop = asyncio.get_event_loop()
        try:
            embedding = await loop.run_in_executor(None, self.model.encode, text)
            return np.array(embedding)
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return np.zeros(self.dimension)
    
    async def embed_batch(self, texts: list, batch_size: int = 32, use_cache: bool = True) -> list:
        """Create embeddings for multiple texts"""
        if not texts:
            return []
        loop = asyncio.get_event_loop()
        try:
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)
            )
            return [np.array(emb) for emb in embeddings]
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return [np.zeros(self.dimension) for _ in texts]

# Global instance
embedder = Embedder()