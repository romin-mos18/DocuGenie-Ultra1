'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Typography,
  Paper,
  Button,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Chip,
  Avatar,
  Grid,
  Divider,
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  Close,
  CheckCircle,
  Error as ErrorIcon,
  Description,
  Image,
  Folder,
  Delete,
  Refresh,
  Upload,
  TableChart,
  DataObject,
  Code,
  Archive,
  Lightbulb,
  Cloud,
} from '@mui/icons-material';

interface UploadFile {
  id: string;
  name: string;
  size: number;
  type: string;
  lastModified: number;
  originalFile: File; // Store the original file for uploads
  preview?: string;
  progress: number;
  error?: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  uploadedAt?: string;
  serverResponse?: any;
}

export default function DocumentUpload() {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [fileTypeFilter, setFileTypeFilter] = useState<string>('all');
  const [uploadStats, setUploadStats] = useState({
    total: 0,
    completed: 0,
    failed: 0,
    inProgress: 0
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    console.log('Accepted files:', acceptedFiles); // Debug log
    
    const newFiles: UploadFile[] = acceptedFiles.map((file, index) => {
      console.log('Processing file:', {
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: file.lastModified
      }); // Debug log
      
      // Create upload file object with original file reference
      const uploadFile: UploadFile = {
        id: `${Date.now()}-${index}`,
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: file.lastModified,
        originalFile: file, // Store the original file
        preview: file.type?.startsWith('image/') ? URL.createObjectURL(file) : undefined,
        progress: 0,
        status: 'pending' as const,
      };
      
      console.log('Created uploadFile:', {
        name: uploadFile.name,
        size: uploadFile.size,
        type: uploadFile.type,
        id: uploadFile.id
      }); // Debug log
      
      return uploadFile;
    });

    setFiles((prevFiles) => [...prevFiles, ...newFiles]);
    setUploadStats(prev => ({
      ...prev,
      total: prev.total + newFiles.length
    }));
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      // PDF Documents
      'application/pdf': ['.pdf'],
      
      // Word and Text Documents
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/rtf': ['.rtf'],
      
      // Spreadsheets
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv'],
      
      // JSON Files
      'application/json': ['.json'],
      
      // Images
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'],
      
      // XML Files
      'application/xml': ['.xml'],
      'text/xml': ['.xml'],
      
      // Additional Text Formats
      'text/html': ['.html', '.htm'],
      'text/css': ['.css'],
      'text/javascript': ['.js'],
      'application/javascript': ['.js'],
      
      // Archive Formats
      'application/zip': ['.zip'],
      'application/x-rar-compressed': ['.rar'],
      'application/x-7z-compressed': ['.7z'],
    },
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: true,
    validator: (file) => {
      // Additional validation for file extensions
      const allowedExtensions = [
        '.pdf', '.doc', '.docx', '.txt', '.md', '.rtf',
        '.xls', '.xlsx', '.csv', '.json', '.xml',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',
        '.html', '.htm', '.css', '.js', '.zip', '.rar', '.7z'
      ];
      
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!allowedExtensions.includes(fileExtension)) {
        return {
          code: 'file-invalid-type',
          message: `File type ${fileExtension} is not supported. Please upload a valid document, image, or data file.`
        };
      }
      
      return null;
    }
  });

  const uploadFile = async (file: UploadFile): Promise<boolean> => {
    console.log('Starting upload for file:', file);
    console.log('Original file object:', file.originalFile);
    console.log('Original file name:', file.originalFile?.name);
    console.log('Original file size:', file.originalFile?.size);
    console.log('Original file type:', file.originalFile?.type);
    
    // Check if originalFile is valid
    if (!file.originalFile || !(file.originalFile instanceof File)) {
      throw new Error('Invalid file object - originalFile is not a File instance');
    }
    
    const formData = new FormData();
    
    // Use the original file for upload
    formData.append('file', file.originalFile);
    
    // Verify what was added to FormData
    console.log('FormData file entry:', formData.get('file'));

    try {
      // Update status to uploading
      setFiles((prevFiles) =>
        prevFiles.map((f) =>
          f.id === file.id
            ? { ...f, status: 'uploading' as const, progress: 10 }
            : f
        )
      );

      // Simulate progress
      const progressInterval = setInterval(() => {
        setFiles((prevFiles) =>
          prevFiles.map((f) =>
            f.id === file.id && f.progress < 90
              ? { ...f, progress: f.progress + 10 }
              : f
          )
        );
      }, 100);

      console.log('Uploading file:', file.name, 'Size:', file.size, 'Type:', file.type);
      console.log('FormData contains:', formData.get('file'));

              const response = await fetch('http://localhost:8007/api/v1/upload', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      console.log('Response status:', response.status, response.statusText);

      if (!response.ok) {
        // Get detailed error message from response
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.text();
          console.log('Error response:', errorData);
          errorMessage = `Upload failed: ${errorData || response.statusText}`;
        } catch (e) {
          console.log('Could not parse error response');
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Upload result:', result); // For debugging

      // Update file status to success with server response data
      setFiles((prevFiles) =>
        prevFiles.map((f) =>
          f.id === file.id
            ? { 
                ...f, 
                progress: 100, 
                status: 'success' as const,
                uploadedAt: new Date().toLocaleTimeString(),
                serverResponse: result
              }
            : f
        )
      );

      setUploadStats(prev => ({
        ...prev,
        completed: prev.completed + 1,
        inProgress: prev.inProgress - 1
      }));

      return true;
    } catch (error) {
      // Update file status to error
      setFiles((prevFiles) =>
        prevFiles.map((f) =>
          f.id === file.id
            ? {
                ...f,
                status: 'error' as const,
                error: error instanceof Error ? error.message : 'Upload failed',
                progress: 0
              }
            : f
        )
      );

      setUploadStats(prev => ({
        ...prev,
        failed: prev.failed + 1,
        inProgress: prev.inProgress - 1
      }));

      return false;
    }
  };

  const uploadAllFiles = async () => {
    const pendingFiles = files.filter(f => f.status === 'pending');
    if (pendingFiles.length === 0) return;

    setUploading(true);
    setUploadStats(prev => ({
      ...prev,
      inProgress: pendingFiles.length
    }));

    // Upload files in batches of 5 to avoid overwhelming the server
    const batchSize = 5;
    for (let i = 0; i < pendingFiles.length; i += batchSize) {
      const batch = pendingFiles.slice(i, i + batchSize);
      await Promise.all(batch.map(file => uploadFile(file)));
    }

    setUploading(false);
  };

  const removeFile = (fileId: string) => {
    setFiles((prevFiles) => {
      const fileToRemove = prevFiles.find(f => f.id === fileId);
      if (fileToRemove) {
        // Only revoke URL if it exists and is a blob URL
        if (fileToRemove.preview && fileToRemove.preview.startsWith('blob:')) {
          try {
            URL.revokeObjectURL(fileToRemove.preview);
          } catch (error) {
            console.warn('Error revoking object URL:', error);
          }
        }
        
        setUploadStats(prev => ({
          total: prev.total - 1,
          completed: fileToRemove.status === 'success' ? prev.completed - 1 : prev.completed,
          failed: fileToRemove.status === 'error' ? prev.failed - 1 : prev.failed,
          inProgress: fileToRemove.status === 'uploading' ? prev.inProgress - 1 : prev.inProgress
        }));
      }
      return prevFiles.filter((f) => f.id !== fileId);
    });
  };

  const clearAllFiles = () => {
    files.forEach(file => {
      if (file.preview && file.preview.startsWith('blob:')) {
        try {
          URL.revokeObjectURL(file.preview);
        } catch (error) {
          console.warn('Error revoking object URL:', error);
        }
      }
    });
    setFiles([]);
    setUploadStats({ total: 0, completed: 0, failed: 0, inProgress: 0 });
  };

  // Test function to verify backend connection
  const testUpload = async () => {
    try {
      console.log('Testing upload...');
      
      // Create a simple test file
      const testContent = 'This is a test file content';
      const testFile = new File([testContent], 'test.txt', { type: 'text/plain' });
      
      console.log('Test file created:', testFile);
      
      const formData = new FormData();
      formData.append('file', testFile);
      
      console.log('FormData created with test file');
      
      const response = await fetch('http://localhost:8007/api/v1/upload', {
        method: 'POST',
        body: formData,
      });
      
      console.log('Test response status:', response.status, response.statusText);
      
      if (response.ok) {
        const result = await response.json();
        console.log('Test upload SUCCESS:', result);
        alert('Test upload successful! Backend is working.');
      } else {
        const errorText = await response.text();
        console.log('Test upload FAILED:', errorText);
        alert(`Test upload failed: ${response.status} ${response.statusText}\nError: ${errorText}`);
      }
    } catch (error) {
      console.error('Test upload error:', error);
      alert(`Test upload error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const retryFailedUploads = () => {
    setFiles(prevFiles =>
      prevFiles.map(f =>
        f.status === 'error'
          ? { ...f, status: 'pending' as const, error: undefined, progress: 0 }
          : f
      )
    );
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (file: UploadFile) => {
    const fileType = file.type || '';
    const fileName = file.name || '';
    const fileExtension = '.' + fileName.split('.').pop()?.toLowerCase();
    
    // Images
    if (fileType.startsWith('image/')) {
      return <Image sx={{ color: '#16a34a' }} />;
    }
    
    // PDF Documents
    if (fileType === 'application/pdf' || fileExtension === '.pdf') {
      return <Description sx={{ color: '#dc2626' }} />;
    }
    
    // Word and Text Documents
    if (fileType.includes('word') || fileType.includes('document') || 
        ['.doc', '.docx', '.txt', '.md', '.rtf'].includes(fileExtension)) {
      return <Description sx={{ color: '#3b82f6' }} />;
    }
    
    // Spreadsheets
    if (fileType.includes('excel') || fileType.includes('spreadsheet') || 
        ['.xls', '.xlsx', '.csv'].includes(fileExtension)) {
      return <TableChart sx={{ color: '#16a34a' }} />;
    }
    
    // JSON Files
    if (fileType === 'application/json' || fileExtension === '.json') {
      return <DataObject sx={{ color: '#ea580c' }} />;
    }
    
    // XML Files
    if (fileType.includes('xml') || fileExtension === '.xml') {
      return <Code sx={{ color: '#7c3aed' }} />;
    }
    
    // Archive Files
    if (fileType.includes('zip') || fileType.includes('rar') || fileType.includes('7z') ||
        ['.zip', '.rar', '.7z'].includes(fileExtension)) {
      return <Archive sx={{ color: '#f59e0b' }} />;
    }
    
    // Code Files
    if (['.html', '.htm', '.css', '.js'].includes(fileExtension)) {
      return <Code sx={{ color: '#059669' }} />;
    }
    
    return <InsertDriveFile sx={{ color: '#6b7280' }} />;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return '#16a34a';
      case 'error': return '#dc2626';
      case 'uploading': return '#f59e0b';
      case 'pending': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getFileCategory = (file: UploadFile) => {
    const fileType = file.type || '';
    const fileName = file.name || '';
    const fileExtension = '.' + fileName.split('.').pop()?.toLowerCase();
    
    // Images
    if (fileType.startsWith('image/') || ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'].includes(fileExtension)) {
      return 'Image';
    }
    
    // PDF Documents
    if (fileType === 'application/pdf' || fileExtension === '.pdf') {
      return 'PDF';
    }
    
    // Word and Text Documents
    if (fileType.includes('word') || fileType.includes('document') || 
        ['.doc', '.docx', '.txt', '.md', '.rtf'].includes(fileExtension)) {
      return 'Document';
    }
    
    // Spreadsheets
    if (fileType.includes('excel') || fileType.includes('spreadsheet') || 
        ['.xls', '.xlsx', '.csv'].includes(fileExtension)) {
      return 'Spreadsheet';
    }
    
    // JSON Files
    if (fileType === 'application/json' || fileExtension === '.json') {
      return 'Data';
    }
    
    // XML Files
    if (fileType.includes('xml') || fileExtension === '.xml') {
      return 'Data';
    }
    
    // Archive Files
    if (fileType.includes('zip') || fileType.includes('rar') || fileType.includes('7z') ||
        ['.zip', '.rar', '.7z'].includes(fileExtension)) {
      return 'Archive';
    }
    
    // Code Files
    if (['.html', '.htm', '.css', '.js'].includes(fileExtension)) {
      return 'Code';
    }
    
    return 'Other';
  };

  const pendingFiles = files.filter(f => f.status === 'pending').length;

  // Filter files by type
  const filteredFiles = fileTypeFilter === 'all' 
    ? files 
    : files.filter(file => getFileCategory(file) === fileTypeFilter);

  // Get unique file categories for filter
  const fileCategories = Array.from(new Set(files.map(file => getFileCategory(file)))).sort();

  return (
    <Box>
      {/* Main Upload Section - Simple Layout */}
      <Grid container spacing={3}>
        {/* Left: Upload Zone (Vertical) */}
        <Grid item xs={12} md={5}>
                              <Paper sx={{ 
            p: 3, 
            backgroundColor: '#ffffff', 
            border: '1px solid #e5e7eb', 
            borderRadius: '8px', 
            boxShadow: 'none',
            height: 'fit-content'
          }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: '6px', 
                backgroundColor: '#dbeafe', 
                mr: 2 
              }}>
                <CloudUpload sx={{ color: '#3b82f6', fontSize: 20 }} />
              </Box>
              <Typography variant="h6" sx={{ color: '#1f2937', fontWeight: 600 }}>
                Document Upload
        </Typography>
            </Box>

            {/* Upload Stats - Simple */}
            {uploadStats.total > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#1f2937', fontWeight: 600, mb: 2 }}>
                  Upload Statistics
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#f8fafc', borderRadius: '6px' }}>
                      <Typography variant="h6" sx={{ color: '#1f2937', fontWeight: 600 }}>
                        {uploadStats.total}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#6b7280' }}>
                        Total Files
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#f0fdf4', borderRadius: '6px' }}>
                      <Typography variant="h6" sx={{ color: '#16a34a', fontWeight: 600 }}>
                        {uploadStats.completed}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#15803d' }}>
                        Completed
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#fef2f2', borderRadius: '6px' }}>
                      <Typography variant="h6" sx={{ color: '#dc2626', fontWeight: 600 }}>
                        {uploadStats.failed}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#b91c1c' }}>
                        Failed
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#fffbeb', borderRadius: '6px' }}>
                      <Typography variant="h6" sx={{ color: '#f59e0b', fontWeight: 600 }}>
                        {uploadStats.inProgress}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#d97706' }}>
                        In Progress
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
                
                {/* File Type Summary */}
                {files.length > 0 && (
                  <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #f1f5f9' }}>
                    <Typography variant="caption" sx={{ color: '#6b7280', fontWeight: 600, display: 'block', mb: 1 }}>
                      File Types:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {fileCategories.map((category) => {
                        const count = files.filter(file => getFileCategory(file) === category).length;
                        return (
                          <Chip
                            key={category}
                            label={`${category}: ${count}`}
                            size="small"
                            sx={{
                              height: '20px',
                              fontSize: '0.65rem',
                              backgroundColor: '#f3f4f6',
                              color: '#374151',
                              fontWeight: 500
                            }}
                          />
                        );
                      })}
                    </Box>
                  </Box>
                )}
              </Box>
            )}

                                    {/* Dropzone - Simple */}
        <Box
          {...getRootProps()}
          sx={{
                border: `2px dashed ${isDragActive ? '#3b82f6' : '#e5e7eb'}`,
                borderRadius: '8px',
                padding: '48px 24px',
            textAlign: 'center',
                backgroundColor: isDragActive ? '#f0f9ff' : '#f8fafc',
            cursor: 'pointer',
                transition: 'all 0.2s ease',
                mb: 3,
            '&:hover': {
                  borderColor: '#3b82f6',
                  backgroundColor: '#f0f9ff',
            },
          }}
        >
          <input {...getInputProps()} />
              <CloudUpload sx={{ fontSize: 48, color: '#3b82f6', mb: 2 }} />
              <Typography variant="h6" sx={{ color: '#1f2937', fontWeight: 600, mb: 1 }}>
                {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
              </Typography>
              <Typography variant="body2" sx={{ color: '#6b7280', mb: 2 }}>
                or click to select files
              </Typography>
              
              {/* Supported File Types */}
              <Box sx={{ 
                display: 'flex', 
                flexWrap: 'wrap', 
                justifyContent: 'center', 
                gap: 1,
                maxWidth: '400px',
                margin: '0 auto'
              }}>
                {['PDF', 'DOC', 'XLS', 'CSV', 'TXT', 'JSON', 'PNG', 'JPG'].map((type) => (
                  <Chip
                    key={type}
                    label={type}
                    size="small"
                    sx={{
                      backgroundColor: '#f3f4f6',
                      color: '#374151',
                      fontSize: '0.7rem',
                      height: '24px',
                      '&:hover': {
                        backgroundColor: '#e5e7eb'
                      }
                    }}
                  />
                ))}
                <Chip
                  label="+ More"
                  size="small"
                  sx={{
                    backgroundColor: '#dbeafe',
                    color: '#1e40af',
                    fontSize: '0.7rem',
                    height: '24px',
                    fontWeight: 600
                  }}
                />
              </Box>
        </Box>

                                    {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
              {/* Test Upload Button - Always visible */}
              <Button
                variant="outlined"
                size="small"
                onClick={testUpload}
                sx={{ 
                  textTransform: 'none',
                  borderColor: '#10b981',
                  color: '#10b981',
                  '&:hover': {
                    borderColor: '#059669',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)'
                  }
                }}
              >
                Test Upload
              </Button>
              
              {files.length > 0 && (
                <>
                  {pendingFiles > 0 && (
                    <Button
                      variant="contained"
                      size="medium"
                      startIcon={<Upload />}
                      onClick={uploadAllFiles}
                      disabled={uploading}
                      sx={{
                        backgroundColor: '#3b82f6',
                        '&:hover': { backgroundColor: '#2563eb' },
                        textTransform: 'none',
                        flex: 1
                      }}
                    >
                      Upload {pendingFiles} Files
                    </Button>
                  )}
                  
                  {uploadStats.failed > 0 && (
                    <Button
                      variant="outlined"
                      size="medium"
                      startIcon={<Refresh />}
                      onClick={retryFailedUploads}
                      sx={{ textTransform: 'none' }}
                    >
                      Retry Failed
                    </Button>
                  )}
                  
                  <IconButton
                    size="small"
                    onClick={clearAllFiles}
                    sx={{ color: '#6b7280' }}
                  >
                    <Delete />
                  </IconButton>
                </>
              )}
            </Box>
          </Paper>
        </Grid>

                {/* Right: File Display */}
        <Grid item xs={12} md={7}>
          {files.length > 0 && (
            <Paper sx={{ 
              p: 3, 
              backgroundColor: '#ffffff', 
              border: '1px solid #e5e7eb', 
              borderRadius: '8px', 
              boxShadow: 'none',
              height: 'fit-content'
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#1f2937', fontWeight: 600 }}>
                  Uploaded Files ({files.length})
                </Typography>
                
                {/* File Type Filter */}
                {files.length > 0 && (
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Typography variant="caption" sx={{ color: '#6b7280', mr: 1 }}>
                      Filter:
                    </Typography>
                    <Chip
                      label="All"
                      size="small"
                      onClick={() => setFileTypeFilter('all')}
                      sx={{
                        backgroundColor: fileTypeFilter === 'all' ? '#3b82f6' : '#f3f4f6',
                        color: fileTypeFilter === 'all' ? 'white' : '#374151',
                        cursor: 'pointer',
                        '&:hover': {
                          backgroundColor: fileTypeFilter === 'all' ? '#2563eb' : '#e5e7eb'
                        }
                      }}
                    />
                    {fileCategories.map((category) => (
                      <Chip
                        key={category}
                        label={category}
                        size="small"
                        onClick={() => setFileTypeFilter(category)}
                        sx={{
                          backgroundColor: fileTypeFilter === category ? '#3b82f6' : '#f3f4f6',
                          color: fileTypeFilter === category ? 'white' : '#374151',
                          cursor: 'pointer',
                          '&:hover': {
                            backgroundColor: fileTypeFilter === category ? '#2563eb' : '#e5e7eb'
                          }
                        }}
                      />
                    ))}
                  </Box>
                )}
              </Box>
              
                            {/* File Grid */}
              <Box sx={{ 
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
                gap: 2,
                maxHeight: 400,
                overflow: 'auto'
              }}>
                {filteredFiles.map((file) => (
                  <Box
                    key={file.id}
                    sx={{
                      border: '1px solid #f1f5f9',
                      borderRadius: '8px',
                      p: 2,
                      backgroundColor: file.status === 'success' ? '#f0fdf4' : 
                                     file.status === 'error' ? '#fef2f2' : 
                                     file.status === 'uploading' ? '#f0f9ff' : '#f8fafc',
                      position: 'relative'
                    }}
                  >
                                        {/* File Icon and Info */}
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                      <Avatar sx={{ 
                        backgroundColor: 'transparent',
                        width: 32,
                        height: 32,
                        mr: 1
                      }}>
                        {getFileIcon(file)}
                      </Avatar>
                      
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: '#1f2937', 
                            fontWeight: 600,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                          title={file.name || 'Unknown file'}
                        >
                          {file.name || 'Unknown file'}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                          <Typography variant="caption" sx={{ color: '#6b7280' }}>
                            {formatFileSize(file.size || 0)}
                          </Typography>
                          <Chip
                            label={getFileCategory(file)}
                            size="small"
                            sx={{
                              height: '18px',
                              fontSize: '0.65rem',
                              backgroundColor: '#f3f4f6',
                              color: '#374151',
                              fontWeight: 500
                            }}
                          />
                        </Box>
                      </Box>

                      <IconButton
                        size="small"
                        onClick={() => removeFile(file.id)}
                        sx={{ color: '#6b7280', ml: 1 }}
                      >
                        <Close />
                      </IconButton>
                    </Box>

                                                            {/* Progress Bar */}
                    {file.status === 'uploading' && (
                      <Box sx={{ mb: 2 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={file.progress} 
                          sx={{
                            height: 6,
                            borderRadius: 3,
                            backgroundColor: '#f1f5f9',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: '#3b82f6',
                              borderRadius: 3,
                            },
                          }}
                        />
                        <Typography variant="caption" sx={{ color: '#6b7280', mt: 0.5 }}>
                          {file.progress}% uploaded
                        </Typography>
                      </Box>
                    )}

                                                            {/* Status and Details */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Chip
                        label={file.status}
                        size="small"
                        icon={
                          file.status === 'success' ? <CheckCircle /> :
                          file.status === 'error' ? <ErrorIcon /> :
                          file.status === 'uploading' ? <Upload /> :
                          undefined
                        }
                        color={
                          file.status === 'success' ? 'success' :
                          file.status === 'error' ? 'error' :
                          file.status === 'uploading' ? 'primary' :
                          'default'
                        }
                        sx={{
                          height: 24,
                          fontWeight: 500,
                          fontSize: '0.7rem'
                        }}
                      />
                    </Box>

                    {/* Server Response Details */}
                    {file.serverResponse && (
                      <Box sx={{ mt: 1, pt: 1, borderTop: '1px solid #f1f5f9' }}>
                        <Typography variant="caption" sx={{ color: '#6b7280', display: 'block' }}>
                          {file.serverResponse.document_type && (
                            <>Type: {file.serverResponse.document_type}<br/></>
                          )}
                          {file.serverResponse.ocr_accuracy && (
                            <>OCR: {file.serverResponse.ocr_accuracy}<br/></>
                          )}
                          {file.uploadedAt && (
                            <>Uploaded: {file.uploadedAt}</>
                          )}
                        </Typography>
                      </Box>
                    )}

                    {/* Error Message */}
                    {file.error && (
                      <Box sx={{ mt: 1, pt: 1, borderTop: '1px solid #f1f5f9' }}>
                        <Typography variant="caption" sx={{ color: '#dc2626' }}>
                          {file.error}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                ))}
                
                {/* Empty state for filtered results */}
                {filteredFiles.length === 0 && files.length > 0 && (
                  <Box sx={{ 
                    textAlign: 'center', 
                    py: 4, 
                    color: 'text.secondary' 
                  }}>
                    <Folder sx={{ fontSize: 48, mb: 2, color: 'text.disabled' }} />
                    <Typography variant="h6" gutterBottom>
                      No {fileTypeFilter === 'all' ? 'files' : fileTypeFilter} found
                    </Typography>
                    <Typography variant="body2">
                      {fileTypeFilter === 'all' 
                        ? 'Try uploading some files first' 
                        : `No ${fileTypeFilter} files match your current filter`
                      }
                    </Typography>
                  </Box>
                )}
              </Box>
            </Paper>
          )}
        </Grid>
      </Grid>

      {/* Three Panel Layout: AI Features, Supported Formats, Service Features */}
      <Box sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', lg: 'row' } }}>
          {/* Panel 1: AI Processing Features */}
          <Paper sx={{ 
            flex: 1,
            p: 3, 
            backgroundColor: '#ffffff', 
            border: '1px solid #e5e7eb', 
            borderRadius: '16px', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Box sx={{ 
                p: 1, 
                borderRadius: '50%', 
                backgroundColor: '#dbeafe', 
                mr: 2 
              }}>
                <Lightbulb sx={{ color: '#3b82f6', fontSize: 20 }} />
              </Box>
              <Typography variant="h6" sx={{ color: '#1f2937', fontWeight: 600 }}>
                AI Processing Features
              </Typography>
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: '50%', 
                    backgroundColor: '#dbeafe'
                  }}>
                    <Description sx={{ color: '#3b82f6', fontSize: 16 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                      OCR Processing
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      99.8% accuracy
                    </Typography>
                  </Box>
                </Box>
                <Chip label="99.8% accuracy" size="small" sx={{ backgroundColor: '#f3f4f6', color: '#6b7280', ml: 4 }} />
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: '50%', 
                    backgroundColor: '#fef3c7'
                  }}>
                    <CheckCircle sx={{ color: '#f59e0b', fontSize: 16 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                      HIPAA Compliant
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      Secure processing
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: '50%', 
                    backgroundColor: '#dcfce7'
                  }}>
                    <Folder sx={{ color: '#16a34a', fontSize: 16 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                      Document Classification
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      Automatic categorization
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: '50%', 
                    backgroundColor: '#fce7f3'
                  }}>
                    <Upload sx={{ color: '#ec4899', fontSize: 16 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                      Fast Processing
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      Average 3.2 seconds
                    </Typography>
                  </Box>
                </Box>
                <Chip label="Avg 3.2s" size="small" sx={{ backgroundColor: '#f3f4f6', color: '#6b7280', ml: 4 }} />
              </Grid>
            </Grid>
          </Paper>

          {/* Panel 2: Supported Formats */}
          <Paper sx={{ 
            flex: 1,
            p: 3, 
            backgroundColor: '#ffffff', 
            border: '1px solid #e5e7eb', 
            borderRadius: '16px', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Box sx={{ 
                p: 1, 
                borderRadius: '50%', 
                backgroundColor: '#f3e8ff', 
                mr: 2 
              }}>
                <Description sx={{ color: '#7c3aed', fontSize: 20 }} />
              </Box>
              <Typography variant="h6" sx={{ color: '#1f2937', fontWeight: 600 }}>
                Supported Formats
              </Typography>
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: '50%', 
                    backgroundColor: '#f3e8ff'
                  }}>
                    <Description sx={{ color: '#7c3aed', fontSize: 16 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                      Documents
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      PDF, DOC, DOCX, TXT, MD, RTF
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: '50%', 
                    backgroundColor: '#dcfce7'
                  }}>
                    <TableChart sx={{ color: '#16a34a', fontSize: 16 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                      Spreadsheets
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      XLS, XLSX, CSV
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: '50%', 
                    backgroundColor: '#fef2f2'
                  }}>
                    <DataObject sx={{ color: '#dc2626', fontSize: 16 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                      Data Files
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      JSON, XML
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: '50%', 
                    backgroundColor: '#dcfce7'
                  }}>
                    <Image sx={{ color: '#16a34a', fontSize: 16 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                      Images
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: '50%', 
                    backgroundColor: '#dbeafe'
                  }}>
                    <Code sx={{ color: '#3b82f6', fontSize: 16 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                      Code Files
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      HTML, CSS, JS
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: '50%', 
                    backgroundColor: '#f3f4f6'
                  }}>
                    <Description sx={{ color: '#6b7280', fontSize: 16 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                      Maximum file size
                    </Typography>
                    <Chip label="100MB" size="small" sx={{ backgroundColor: '#f3f4f6', color: '#6b7280' }} />
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* Panel 3: Service Features */}
          <Paper sx={{ 
            flex: 1,
            p: 3, 
            backgroundColor: '#f0f9ff', 
            border: '1px solid #bae6fd', 
            borderRadius: '16px', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Box sx={{ 
                p: 1, 
                borderRadius: '50%', 
                backgroundColor: '#dbeafe', 
                mr: 2 
              }}>
                <Cloud sx={{ color: '#3b82f6', fontSize: 20 }} />
              </Box>
              <Typography variant="h6" sx={{ color: '#1f2937', fontWeight: 600 }}>
                Service Features
              </Typography>
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#3b82f6' }} />
                  <Typography variant="body2" color="text.primary" fontWeight="500">
                    Unlimited files
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#3b82f6' }} />
                  <Typography variant="body2" color="text.primary" fontWeight="500">
                    Batch processing
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#3b82f6' }} />
                  <Typography variant="body2" color="text.primary" fontWeight="500">
                    Real-time progress tracking
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#3b82f6' }} />
                  <Typography variant="body2" color="text.primary" fontWeight="500">
                    Automatic backup
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#3b82f6' }} />
                  <Typography variant="body2" color="text.primary" fontWeight="500">
                    99.9% uptime guarantee
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Box>
      </Box>
    </Box>
  );
}