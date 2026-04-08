import { useState, useCallback } from 'react';
import { uploadDocument, getDocuments, deleteDocument } from '../services/api';
import { DocumentUpload } from '../types';

export function useFileUpload() {
  const [documents, setDocuments] = useState<DocumentUpload[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedDocument, setSelectedDocument] = useState<DocumentUpload | null>(null);

  const loadDocuments = useCallback(async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  }, []);

  const uploadFile = useCallback(async (file: File) => {
    setUploading(true);
    setUploadProgress(0);
    
    try {
      const result = await uploadDocument(file, (progress) => {
        setUploadProgress(progress);
      });
      
      const newDoc: DocumentUpload = {
        id: result.document_id,
        filename: result.filename,
        size: file.size,
        type: file.type,
        status: 'completed',
        progress: 100,
        pages: result.pages,
        chunks: result.chunks,
        created_at: new Date().toISOString(),
      };
      
      setDocuments(prev => [...prev, newDoc]);
      setSelectedDocument(newDoc);
      
      return newDoc;
    } catch (error) {
      console.error('Upload failed:', error);
      throw error;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, []);

  const removeDocument = useCallback(async (id: string) => {
    try {
      await deleteDocument(id);
      setDocuments(prev => prev.filter(doc => doc.id !== id));
      if (selectedDocument?.id === id) {
        setSelectedDocument(null);
      }
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  }, [selectedDocument]);

  return {
    documents,
    uploading,
    uploadProgress,
    selectedDocument,
    setSelectedDocument,
    uploadFile,
    removeDocument,
    loadDocuments,
  };
}