"""
Simple Vector Store Module (No FAISS required)
Uses numpy arrays for similarity search
"""

import numpy as np
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import asyncio
from datetime import datetime

from app.config import config
from app.document_processor.embedder import embedder
from app.utils.logger import logger

class VectorStore:
    """
    Simple vector store using numpy for similarity search
    (Fallback when FAISS is not available)
    """
    
    def __init__(self):
        self.vectors = []  # List of numpy arrays
        self.metadata = []
        self.dimension = embedder.dimension
        self.index_path = config.VECTOR_STORE_DIR / "vectors.npy"
        self.metadata_path = config.VECTOR_STORE_DIR / "metadata.json"
        self.lock = asyncio.Lock()  # Prevent concurrent writes
        self.load()
    
    def load(self):
        """Load existing vectors if available"""
        if self.index_path.exists():
            try:
                self.vectors = list(np.load(self.index_path, allow_pickle=True))
                logger.info(f"Loaded {len(self.vectors)} vectors")
            except Exception as e:
                logger.error(f"Failed to load vectors: {e}")
                self.vectors = []
        
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded {len(self.metadata)} metadata entries")
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
                self.metadata = []
    
    async def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        user_id: str,
        document_id: str
    ):
        """Add chunks to vector store"""
        texts = [c['text'] for c in chunks]
        
        # Generate embeddings
        embeddings = await embedder.embed_batch(texts)
        
        async with self.lock:
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                self.vectors.append(emb)
                self.metadata.append({
                    'id': f"{document_id}_{i}",
                    'document_id': document_id,
                    'user_id': user_id,
                    'text': chunk['text'],
                    'chunk_index': chunk.get('chunk_index', i),
                    'metadata': chunk.get('metadata', {}),
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Save
            self.save()
            logger.info(f"Added {len(chunks)} chunks to vector store")
    
    async def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        if not self.vectors:
            return []
        
        # Generate query embedding
        query_emb = await embedder.embed(query)
        
        # Calculate similarities safely
        similarities = []
        norm_q = np.linalg.norm(query_emb)
        
        for i, vec in enumerate(self.vectors):
            # Skip if query embedding is zero
            if norm_q == 0:
                similarity = 0.0
            else:
                norm_v = np.linalg.norm(vec)
                if norm_v == 0:
                    similarity = 0.0
                else:
                    similarity = np.dot(query_emb, vec) / (norm_q * norm_v)
            
            # Filter by user if specified
            if user_id and self.metadata[i]['user_id'] != user_id:
                continue
            
            similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top k
        results = []
        for i, score in similarities[:k]:
            meta = self.metadata[i]
            results.append({
                'text': meta['text'],
                'score': float(score),
                'document_id': meta['document_id'],
                'metadata': meta['metadata'],
                'id': meta['id']
            })
        
        return results
    
    async def search_document(
        self,
        document_id: str,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search within specific document"""
        # Filter by document_id first
        doc_indices = [
            i for i, m in enumerate(self.metadata)
            if m['document_id'] == document_id
        ]
        
        if not doc_indices:
            return []
        
        # Generate query embedding
        query_emb = await embedder.embed(query)
        norm_q = np.linalg.norm(query_emb)
        
        # Calculate similarities only for this document
        similarities = []
        for i in doc_indices:
            vec = self.vectors[i]
            if norm_q == 0:
                similarity = 0.0
            else:
                norm_v = np.linalg.norm(vec)
                if norm_v == 0:
                    similarity = 0.0
                else:
                    similarity = np.dot(query_emb, vec) / (norm_q * norm_v)
            similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top k
        results = []
        for i, score in similarities[:k]:
            meta = self.metadata[i]
            results.append({
                'text': meta['text'],
                'score': float(score),
                'metadata': meta['metadata'],
                'id': meta['id']
            })
        
        return results
    
    async def delete_document(self, document_id: str):
        """Delete all chunks for a document"""
        async with self.lock:
            indices_to_keep = [
                i for i, m in enumerate(self.metadata)
                if m['document_id'] != document_id
            ]
            
            if len(indices_to_keep) == len(self.metadata):
                return  # No document found
            
            # Keep only the vectors and metadata we want
            self.vectors = [self.vectors[i] for i in indices_to_keep]
            self.metadata = [self.metadata[i] for i in indices_to_keep]
            
            self.save()
            logger.info(f"Deleted document {document_id} from vector store")
    
    def save(self):
        """Save vectors and metadata to disk"""
        try:
            # Save vectors as a single 2D float32 array for efficiency
            if self.vectors:
                # Convert list of arrays to 2D numpy array
                vectors_array = np.vstack(self.vectors).astype(np.float32)
                np.save(self.index_path, vectors_array)
            else:
                if self.index_path.exists():
                    self.index_path.unlink()
            
            # Save metadata
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, default=str)
            
            logger.info(f"Saved vector store with {len(self.vectors)} vectors")
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'total_vectors': len(self.vectors),
            'dimension': self.dimension,
            'total_documents': len(set(m['document_id'] for m in self.metadata)),
            'total_users': len(set(m['user_id'] for m in self.metadata))
        }

# Global instance
vector_store = VectorStore()