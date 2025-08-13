"""
File Storage Service using MinIO for real file storage
"""
import os
import logging
from typing import Dict, List, Optional, BinaryIO
from pathlib import Path
import hashlib
from datetime import datetime, timedelta
import mimetypes

# MinIO imports
try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    print("⚠️ MinIO not available. Please install: pip install minio")

# Local file system fallback
import shutil
import tempfile

from core.config import settings

logger = logging.getLogger(__name__)

class FileStorageService:
    """File storage service using MinIO with local fallback"""
    
    def __init__(self):
        """Initialize file storage service"""
        self.minio_client = None
        self.minio_available = MINIO_AVAILABLE
        self.local_storage_path = "./uploads"
        
        # Ensure local storage directory exists
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        if self.minio_available:
            try:
                # Initialize MinIO client
                self.minio_client = Minio(
                    endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
                    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
                    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
                    secure=os.getenv("MINIO_SECURE", "false").lower() == "true"
                )
                
                # Ensure bucket exists
                bucket_name = os.getenv("MINIO_BUCKET", "docugenie")
                if not self.minio_client.bucket_exists(bucket_name):
                    self.minio_client.make_bucket(bucket_name)
                    logger.info(f"✅ Created MinIO bucket: {bucket_name}")
                
                logger.info("✅ MinIO file storage service initialized successfully")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize MinIO: {e}")
                self.minio_client = None
                self.minio_available = False
        else:
            logger.info("ℹ️ MinIO not available. Using local file system storage.")
    
    def store_file(self, file_data: BinaryIO, filename: str, content_type: str = None) -> Dict:
        """
        Store a file using MinIO or local storage
        
        Args:
            file_data: File data stream
            filename: Name of the file
            content_type: MIME type of the file
            
        Returns:
            Dict containing storage information
        """
        try:
            # Generate unique file ID
            file_id = self._generate_file_id(filename)
            
            # Determine content type if not provided
            if not content_type:
                content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            
            # Store file
            if self.minio_available and self.minio_client:
                return self._store_in_minio(file_data, file_id, filename, content_type)
            else:
                return self._store_locally(file_data, file_id, filename, content_type)
                
        except Exception as e:
            logger.error(f"Error storing file {filename}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_id": None,
                "storage_path": None
            }
    
    def _store_in_minio(self, file_data: BinaryIO, file_id: str, filename: str, content_type: str) -> Dict:
        """Store file in MinIO"""
        try:
            bucket_name = os.getenv("MINIO_BUCKET", "docugenie")
            
            # Store file in MinIO
            self.minio_client.put_object(
                bucket_name,
                file_id,
                file_data,
                length=-1,  # Unknown length
                content_type=content_type,
                metadata={
                    "original_filename": filename,
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "content_type": content_type
                }
            )
            
            # Generate presigned URL for access
            presigned_url = self.minio_client.presigned_get_object(
                bucket_name,
                file_id,
                expires=timedelta(hours=24)  # 24 hour expiry
            )
            
            return {
                "success": True,
                "file_id": file_id,
                "storage_path": f"minio://{bucket_name}/{file_id}",
                "storage_type": "minio",
                "presigned_url": presigned_url,
                "bucket": bucket_name,
                "object_key": file_id,
                "content_type": content_type,
                "metadata": {
                    "original_filename": filename,
                    "uploaded_at": datetime.utcnow().isoformat()
                }
            }
            
        except S3Error as e:
            logger.error(f"MinIO storage error: {e}")
            return {
                "success": False,
                "error": f"MinIO storage failed: {str(e)}",
                "file_id": file_id,
                "storage_path": None
            }
    
    def _store_locally(self, file_data: BinaryIO, file_id: str, filename: str, content_type: str) -> Dict:
        """Store file locally as fallback"""
        try:
            # Create file path
            file_path = os.path.join(self.local_storage_path, file_id)
            
            # Save file
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file_data, f)
            
            return {
                "success": True,
                "file_id": file_id,
                "storage_path": file_path,
                "storage_type": "local",
                "local_path": file_path,
                "content_type": content_type,
                "metadata": {
                    "original_filename": filename,
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "storage_method": "local_fallback"
                }
            }
            
        except Exception as e:
            logger.error(f"Local storage error: {e}")
            return {
                "success": False,
                "error": f"Local storage failed: {str(e)}",
                "file_id": file_id,
                "storage_path": None
            }
    
    def retrieve_file(self, file_id: str) -> Dict:
        """
        Retrieve a file from storage
        
        Args:
            file_id: ID of the file to retrieve
            
        Returns:
            Dict containing file data and metadata
        """
        try:
            if self.minio_available and self.minio_client:
                return self._retrieve_from_minio(file_id)
            else:
                return self._retrieve_locally(file_id)
                
        except Exception as e:
            logger.error(f"Error retrieving file {file_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_data": None,
                "metadata": None
            }
    
    def _retrieve_from_minio(self, file_id: str) -> Dict:
        """Retrieve file from MinIO"""
        try:
            bucket_name = os.getenv("MINIO_BUCKET", "docugenie")
            
            # Get object info
            obj_info = self.minio_client.stat_object(bucket_name, file_id)
            
            # Get object data
            obj_data = self.minio_client.get_object(bucket_name, file_id)
            
            return {
                "success": True,
                "file_data": obj_data,
                "metadata": {
                    "content_type": obj_info.content_type,
                    "size": obj_info.size,
                    "last_modified": obj_info.last_modified,
                    "etag": obj_info.etag,
                    "user_metadata": obj_info.metadata
                }
            }
            
        except S3Error as e:
            logger.error(f"MinIO retrieval error: {e}")
            return {
                "success": False,
                "error": f"MinIO retrieval failed: {str(e)}",
                "file_data": None,
                "metadata": None
            }
    
    def _retrieve_locally(self, file_id: str) -> Dict:
        """Retrieve file from local storage"""
        try:
            file_path = os.path.join(self.local_storage_path, file_id)
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "File not found",
                    "file_data": None,
                    "metadata": None
                }
            
            # Get file info
            stat_info = os.stat(file_path)
            
            # Read file data
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            return {
                "success": True,
                "file_data": file_data,
                "metadata": {
                    "size": stat_info.st_size,
                    "last_modified": datetime.fromtimestamp(stat_info.st_mtime),
                    "local_path": file_path
                }
            }
            
        except Exception as e:
            logger.error(f"Local retrieval error: {e}")
            return {
                "success": False,
                "error": f"Local retrieval failed: {str(e)}",
                "file_data": None,
                "metadata": None
            }
    
    def delete_file(self, file_id: str) -> Dict:
        """
        Delete a file from storage
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            Dict containing deletion status
        """
        try:
            if self.minio_available and self.minio_client:
                return self._delete_from_minio(file_id)
            else:
                return self._delete_locally(file_id)
                
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _delete_from_minio(self, file_id: str) -> Dict:
        """Delete file from MinIO"""
        try:
            bucket_name = os.getenv("MINIO_BUCKET", "docugenie")
            self.minio_client.remove_object(bucket_name, file_id)
            
            return {
                "success": True,
                "message": f"File {file_id} deleted from MinIO successfully"
            }
            
        except S3Error as e:
            logger.error(f"MinIO deletion error: {e}")
            return {
                "success": False,
                "error": f"MinIO deletion failed: {str(e)}"
            }
    
    def _delete_locally(self, file_id: str) -> Dict:
        """Delete file from local storage"""
        try:
            file_path = os.path.join(self.local_storage_path, file_id)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    "success": True,
                    "message": f"File {file_id} deleted from local storage successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "File not found"
                }
                
        except Exception as e:
            logger.error(f"Local deletion error: {e}")
            return {
                "success": False,
                "error": f"Local deletion failed: {str(e)}"
            }
    
    def list_files(self, prefix: str = "", limit: int = 100) -> Dict:
        """
        List files in storage
        
        Args:
            prefix: Prefix to filter files
            limit: Maximum number of files to return
            
        Returns:
            Dict containing list of files
        """
        try:
            if self.minio_available and self.minio_client:
                return self._list_minio_files(prefix, limit)
            else:
                return self._list_local_files(prefix, limit)
                
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return {
                "success": False,
                "error": str(e),
                "files": []
            }
    
    def _list_minio_files(self, prefix: str, limit: int) -> Dict:
        """List files in MinIO"""
        try:
            bucket_name = os.getenv("MINIO_BUCKET", "docugenie")
            
            objects = self.minio_client.list_objects(bucket_name, prefix=prefix, recursive=True)
            files = []
            
            for obj in objects:
                if len(files) >= limit:
                    break
                    
                files.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                })
            
            return {
                "success": True,
                "files": files,
                "total": len(files),
                "storage_type": "minio"
            }
            
        except S3Error as e:
            logger.error(f"MinIO listing error: {e}")
            return {
                "success": False,
                "error": f"MinIO listing failed: {str(e)}",
                "files": []
            }
    
    def _list_local_files(self, prefix: str, limit: int) -> Dict:
        """List files in local storage"""
        try:
            files = []
            storage_path = Path(self.local_storage_path)
            
            for file_path in storage_path.glob(f"{prefix}*"):
                if len(files) >= limit:
                    break
                    
                if file_path.is_file():
                    stat_info = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "size": stat_info.st_size,
                        "last_modified": datetime.fromtimestamp(stat_info.st_mtime),
                        "path": str(file_path)
                    })
            
            return {
                "success": True,
                "files": files,
                "total": len(files),
                "storage_type": "local"
            }
            
        except Exception as e:
            logger.error(f"Local listing error: {e}")
            return {
                "success": False,
                "error": f"Local listing failed: {str(e)}",
                "files": []
            }
    
    def _generate_file_id(self, filename: str) -> str:
        """Generate unique file ID with safe characters for Windows"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
        
        # Clean filename for Windows compatibility
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        safe_filename = safe_filename[:50]  # Limit length
        
        return f"{timestamp}_{filename_hash}_{safe_filename}"
    
    def get_storage_status(self) -> Dict:
        """Get storage service status"""
        return {
            "service_name": "FileStorageService",
            "minio_available": self.minio_available,
            "local_storage_path": self.local_storage_path,
            "storage_methods": {
                "primary": "MinIO" if self.minio_available else "Local File System",
                "fallback": "Local File System" if self.minio_available else "None"
            },
            "minio_config": {
                "endpoint": os.getenv("MINIO_ENDPOINT", "localhost:9000"),
                "bucket": os.getenv("MINIO_BUCKET", "docugenie"),
                "secure": os.getenv("MINIO_SECURE", "false").lower() == "true"
            } if self.minio_available else None
        }
    
    def cleanup_old_files(self, days_old: int = 30) -> Dict:
        """
        Clean up old files from storage
        
        Args:
            days_old: Files older than this many days will be deleted
            
        Returns:
            Dict containing cleanup results
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            deleted_count = 0
            
            if self.minio_available and self.minio_client:
                # MinIO cleanup would require listing and checking dates
                # For now, return not implemented
                return {
                    "success": False,
                    "error": "MinIO cleanup not implemented yet",
                    "deleted_count": 0
                }
            else:
                # Local cleanup
                storage_path = Path(self.local_storage_path)
                
                for file_path in storage_path.iterdir():
                    if file_path.is_file():
                        file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_age < cutoff_date:
                            try:
                                file_path.unlink()
                                deleted_count += 1
                            except Exception as e:
                                logger.warning(f"Failed to delete old file {file_path}: {e}")
                
                return {
                    "success": True,
                    "deleted_count": deleted_count,
                    "cutoff_date": cutoff_date.isoformat(),
                    "message": f"Cleaned up {deleted_count} old files"
                }
                
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return {
                "success": False,
                "error": str(e),
                "deleted_count": 0
            }
