"""
Document Processing Tasks
Background document processing
"""

from celery import shared_task
from app.document_processor.processor import DocumentProcessor
from app.utils.logger import logger

@shared_task(bind=True, name='process_document')
def process_document(self, document_id: str, user_id: str):
    """
    Process document in background
    """
    logger.info(f"Starting document processing: {document_id}")
    
    processor = DocumentProcessor()
    
    try:
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'progress': 10, 'status': 'Loading document'}
        )
        
        # Process document
        result = processor.process(document_id, user_id)
        
        self.update_state(
            state='PROGRESS',
            meta={'progress': 100, 'status': 'Completed'}
        )
        
        logger.info(f"Document processing completed: {document_id}")
        
        return {
            'status': 'success',
            'document_id': document_id,
            'result': result
        }
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        # Retry on certain errors
        if 'timeout' in str(e).lower():
            raise self.retry(exc=e, countdown=60, max_retries=3)
        
        return {
            'status': 'failed',
            'document_id': document_id,
            'error': str(e)
        }

@shared_task(name='reprocess_failed_documents')
def reprocess_failed_documents():
    """
    Reprocess documents that failed
    """
    from app.database.repositories.document_repo import DocumentRepository
    
    repo = DocumentRepository()
    failed_docs = repo.get_many(status='failed')
    
    for doc in failed_docs:
        process_document.delay(doc['id'], doc['user_id'])
    
    return {'reprocessed': len(failed_docs)}