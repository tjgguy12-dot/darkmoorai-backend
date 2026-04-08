"""
Document Routes with Multi-File Upload Support
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
import uuid
from pathlib import Path
import aiofiles
import asyncio

from app.document_processor.loader import DocumentLoader
from app.document_processor.chunker import TextChunker
from app.document_processor.embedder import embedder
from app.document_processor.vector_store import vector_store
from app.api.dependencies.auth import get_current_user
from app.config import config
from app.utils.logger import logger

router = APIRouter()
loader = DocumentLoader()
chunker = TextChunker()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a single document"""
    return await process_single_file(file, current_user)


@router.post("/upload-multiple")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload multiple documents at once
    Returns document IDs for each file
    """
    results = []
    
    for file in files:
        try:
            result = await process_single_file(file, current_user)
            results.append(result)
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    successful = [r for r in results if r.get("status") == "completed"]
    failed = [r for r in results if r.get("status") == "failed"]
    
    return {
        "total": len(files),
        "successful": len(successful),
        "failed": len(failed),
        "results": results
    }


@router.post("/upload-batch")
async def upload_batch(
    files: List[UploadFile] = File(...),
    batch_name: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload multiple documents as a batch group
    Returns a batch_id for querying across all documents
    """
    batch_id = str(uuid.uuid4())
    document_ids = []
    results = []
    
    for file in files:
        try:
            result = await process_single_file(file, current_user, batch_id=batch_id)
            results.append(result)
            if result.get("status") == "completed":
                document_ids.append(result["document_id"])
        except Exception as e:
            logger.error(f"Failed to upload {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "batch_id": batch_id,
        "batch_name": batch_name or f"Batch_{batch_id[:8]}",
        "document_count": len(document_ids),
        "document_ids": document_ids,
        "results": results,
        "message": f"Uploaded {len(document_ids)} documents. Use batch_id to query all."
    }


async def process_single_file(file: UploadFile, current_user: dict, batch_id: str = None) -> dict:
    """Process a single uploaded file"""
    
    logger.info(f"Uploading: {file.filename} for user {current_user['id']}")
    
    # Validate file
    ext = Path(file.filename).suffix.lower()
    allowed = [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt", ".jpg", ".jpeg", ".png"]
    if ext not in allowed:
        return {
            "filename": file.filename,
            "status": "failed",
            "error": f"File type {ext} not supported"
        }
    
    document_id = str(uuid.uuid4())
    temp_path = config.UPLOAD_DIR / f"{document_id}{ext}"
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Save file
        content = await file.read()
        async with aiofiles.open(temp_path, "wb") as f:
            await f.write(content)
        
        # Load document
        doc_data = await loader.load(temp_path)
        
        # Chunk document
        chunks = chunker.chunk_document(doc_data['text'], metadata={
            'filename': file.filename,
            'document_id': document_id,
            'user_id': current_user['id'],
            'batch_id': batch_id or document_id,
            'file_size': len(content),
            'pages': doc_data['metadata'].get('pages', 1),
            'uploaded_at': str(uuid.uuid4())
        })
        
        # Store in vector database
        await vector_store.add_chunks(chunks, current_user['id'], document_id)
        
        logger.info(f"Document processed: {document_id}, chunks: {len(chunks)}")
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "completed",
            "chunks": len(chunks),
            "pages": doc_data['metadata'].get('pages', 1),
            "batch_id": batch_id,
            "message": "Document uploaded and processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Document processing error: {e}")
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "failed",
            "error": str(e)
        }
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.get("/")
async def get_documents(current_user: dict = Depends(get_current_user)):
    """Get all user documents"""
    docs = {}
    for meta in vector_store.metadata:
        if meta.get('user_id') == current_user['id']:
            doc_id = meta['document_id']
            if doc_id not in docs:
                docs[doc_id] = {
                    "document_id": doc_id,
                    "filename": meta.get('metadata', {}).get('filename', 'Unknown'),
                    "chunks": 0,
                    "batch_id": meta.get('metadata', {}).get('batch_id'),
                    "uploaded_at": meta.get('metadata', {}).get('uploaded_at')
                }
            docs[doc_id]["chunks"] += 1
    
    return {"documents": list(docs.values()), "total": len(docs)}


@router.get("/batches")
async def get_batches(current_user: dict = Depends(get_current_user)):
    """Get all batch groups for user"""
    batches = {}
    for meta in vector_store.metadata:
        if meta.get('user_id') == current_user['id']:
            batch_id = meta.get('metadata', {}).get('batch_id')
            if batch_id and batch_id not in batches:
                batches[batch_id] = {
                    "batch_id": batch_id,
                    "document_count": 0,
                    "documents": []
                }
            if batch_id:
                batches[batch_id]["document_count"] += 1
                doc_info = {
                    "document_id": meta['document_id'],
                    "filename": meta.get('metadata', {}).get('filename')
                }
                if doc_info not in batches[batch_id]["documents"]:
                    batches[batch_id]["documents"].append(doc_info)
    
    return {"batches": list(batches.values())}


@router.get("/batch/{batch_id}")
async def get_batch_documents(
    batch_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all documents in a batch"""
    docs = []
    for meta in vector_store.metadata:
        if (meta.get('user_id') == current_user['id'] and 
            meta.get('metadata', {}).get('batch_id') == batch_id):
            doc_id = meta['document_id']
            if doc_id not in [d['document_id'] for d in docs]:
                docs.append({
                    "document_id": doc_id,
                    "filename": meta.get('metadata', {}).get('filename', 'Unknown'),
                    "chunks": sum(1 for m in vector_store.metadata 
                                 if m['document_id'] == doc_id)
                })
    
    return {
        "batch_id": batch_id,
        "documents": docs,
        "total_documents": len(docs)
    }


@router.get("/{document_id}")
async def get_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Get document details"""
    chunks = []
    filename = "Unknown"
    
    for meta in vector_store.metadata:
        if meta['document_id'] == document_id and meta['user_id'] == current_user['id']:
            chunks.append({
                "chunk_index": meta.get('chunk_index', 0),
                "text_preview": meta['text'][:200],
                "word_count": len(meta['text'].split())
            })
            filename = meta.get('metadata', {}).get('filename', 'Unknown')
    
    if not chunks:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": document_id,
        "filename": filename,
        "total_chunks": len(chunks),
        "chunks": chunks
    }


@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a single document"""
    # Verify ownership
    for meta in vector_store.metadata:
        if meta['document_id'] == document_id and meta['user_id'] == current_user['id']:
            await vector_store.delete_document(document_id)
            return {"message": f"Document {document_id} deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Document not found")


@router.delete("/batch/{batch_id}")
async def delete_batch(
    batch_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete all documents in a batch"""
    deleted = 0
    for meta in vector_store.metadata[:]:  # Iterate over copy
        if (meta.get('user_id') == current_user['id'] and 
            meta.get('metadata', {}).get('batch_id') == batch_id):
            await vector_store.delete_document(meta['document_id'])
            deleted += 1
    
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return {"message": f"Deleted {deleted} documents from batch {batch_id}"}