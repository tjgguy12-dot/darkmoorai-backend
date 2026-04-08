import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileUploaderProps {
  onUpload: (file: File) => Promise<void>;
  maxSize?: number; // in bytes
}

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB default for faster processing

const FileUploader: React.FC<FileUploaderProps> = ({ 
  onUpload, 
  maxSize = MAX_FILE_SIZE 
}) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: any[]) => {
    // Handle rejected files
    if (rejectedFiles && rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0].code === 'file-too-large') {
        setError(`File too large. Maximum size is ${maxSize / 1024 / 1024}MB.`);
      } else if (rejection.errors[0].code === 'file-invalid-type') {
        setError('File type not supported. Please upload PDF, DOCX, XLSX, TXT, or images.');
      } else {
        setError(rejection.errors[0].message);
      }
      return;
    }

    const file = acceptedFiles[0];
    if (!file) return;

    // Check file size
    if (file.size > maxSize) {
      setError(`File too large. Maximum size is ${maxSize / 1024 / 1024}MB. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB`);
      return;
    }

    setFileName(file.name);
    setUploading(true);
    setError(null);
    setUploadProgress(0);
    
    try {
      await onUpload(file);
      setUploadProgress(100);
    } catch (err: any) {
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  }, [onUpload, maxSize]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/plain': ['.txt'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxSize: maxSize,
    maxFiles: 1,
    multiple: false,
  });

  const getFileIcon = (fileName: string | null) => {
    if (!fileName) return '📄';
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf': return '📕';
      case 'docx':
      case 'doc': return '📘';
      case 'xlsx':
      case 'xls': return '📗';
      case 'txt': return '📃';
      case 'jpg':
      case 'jpeg':
      case 'png': return '🖼️';
      default: return '📄';
    }
  };

  return (
    <div className="file-uploader">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${isDragReject ? 'reject' : ''} ${uploading ? 'uploading' : ''}`}
      >
        <input {...getInputProps()} />
        
        {uploading ? (
          <div className="upload-progress">
            <div className="upload-spinner">⏳</div>
            <div className="progress-bar-container">
              <div 
                className="progress-bar" 
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <div className="upload-status">
              {uploadProgress < 100 ? `Uploading... ${uploadProgress}%` : 'Processing...'}
            </div>
            <div className="file-name">{fileName}</div>
          </div>
        ) : isDragActive ? (
          <div className="drag-active">
            <div className="drag-icon">📂</div>
            <p>Drop your file here...</p>
          </div>
        ) : isDragReject ? (
          <div className="drag-reject">
            <div className="reject-icon">❌</div>
            <p>File type not supported</p>
            <small>Please upload PDF, DOCX, XLSX, TXT, or images (max {maxSize / 1024 / 1024}MB)</small>
          </div>
        ) : (
          <div className="drag-default">
            <div className="upload-icon">📎</div>
            <p>Drag & drop or click to upload</p>
            <small>
              Supports: PDF, DOCX, XLSX, TXT, Images (max {maxSize / 1024 / 1024}MB)
            </small>
          </div>
        )}
      </div>
      
      {error && (
        <div className="upload-error">
          <span>⚠️</span> {error}
        </div>
      )}
      
      {fileName && !uploading && !error && (
        <div className="upload-success">
          <span>✅</span> File "{fileName}" uploaded successfully!
        </div>
      )}
    </div>
  );
};

export default FileUploader;