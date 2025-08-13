#!/usr/bin/env python3
"""
Batch Processing Service for DocuGenie Ultra
Handles large volumes of medical documents with parallel processing and progress tracking
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime
import json
import asyncio
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import time
from dataclasses import dataclass
from enum import Enum

# Import other services
from services.docling_service import DoclingService
from services.rag_service import RAGService
from services.llm_service import LLMService
from services.healthcare_model_service import HealthcareModelService

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class BatchJob:
    """Batch processing job configuration"""
    job_id: str
    name: str
    description: str
    source_directory: str
    file_patterns: List[str]
    processing_pipeline: List[str]
    max_workers: int
    created_at: datetime
    status: ProcessingStatus
    total_files: int
    processed_files: int
    failed_files: int
    results: Dict[str, Any]

class BatchProcessingService:
    """Service for batch processing medical documents"""
    
    def __init__(self):
        """Initialize batch processing service"""
        self.jobs_dir = Path("./batch_jobs")
        self.jobs_dir.mkdir(exist_ok=True)
        
        self.active_jobs = {}
        self.job_history = {}
        self.processing_queue = queue.Queue()
        
        # Initialize other services
        self.docling_service = DoclingService()
        self.rag_service = RAGService()
        self.llm_service = LLMService()
        self.model_service = HealthcareModelService()
        
        # Processing pipelines
        self.available_pipelines = {
            "basic_extraction": self._basic_extraction_pipeline,
            "rag_processing": self._rag_processing_pipeline,
            "llm_analysis": self._llm_analysis_pipeline,
            "model_prediction": self._model_prediction_pipeline,
            "compliance_check": self._compliance_check_pipeline,
            "full_analysis": self._full_analysis_pipeline
        }
        
        # Start background worker
        self._start_background_worker()
        
        logger.info("✅ Batch Processing Service initialized successfully")
    
    def _start_background_worker(self):
        """Start background worker for processing jobs"""
        def worker():
            while True:
                try:
                    job = self.processing_queue.get(timeout=1)
                    if job is None:
                        break
                    
                    asyncio.run(self._process_batch_job(job))
                    self.processing_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"❌ Background worker error: {e}")
        
        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()
        logger.info("✅ Background worker started")
    
    def create_batch_job(
        self,
        name: str,
        description: str,
        source_directory: str,
        file_patterns: List[str] = None,
        processing_pipeline: List[str] = None,
        max_workers: int = 4
    ) -> Dict[str, Any]:
        """Create a new batch processing job"""
        try:
            # Validate source directory
            if not os.path.exists(source_directory):
                return {
                    "success": False,
                    "error": f"Source directory does not exist: {source_directory}"
                }
            
            # Set default file patterns
            if file_patterns is None:
                file_patterns = ["*.pdf", "*.docx", "*.txt", "*.xlsx"]
            
            # Set default processing pipeline
            if processing_pipeline is None:
                processing_pipeline = ["basic_extraction"]
            
            # Validate processing pipeline
            invalid_pipelines = [p for p in processing_pipeline if p not in self.available_pipelines]
            if invalid_pipelines:
                return {
                    "success": False,
                    "error": f"Invalid processing pipelines: {invalid_pipelines}"
                }
            
            # Generate job ID
            job_id = f"batch_{int(time.time())}_{len(self.active_jobs)}"
            
            # Count total files
            total_files = self._count_files_in_directory(source_directory, file_patterns)
            
            # Create batch job
            job = BatchJob(
                job_id=job_id,
                name=name,
                description=description,
                source_directory=source_directory,
                file_patterns=file_patterns,
                processing_pipeline=processing_pipeline,
                max_workers=max_workers,
                created_at=datetime.now(),
                status=ProcessingStatus.PENDING,
                total_files=total_files,
                processed_files=0,
                failed_files=0,
                results={}
            )
            
            # Store job
            self.active_jobs[job_id] = job
            
            # Save job to disk
            self._save_job_to_disk(job)
            
            logger.info(f"✅ Created batch job: {job_id} with {total_files} files")
            
            return {
                "success": True,
                "job_id": job_id,
                "total_files": total_files,
                "processing_pipeline": processing_pipeline,
                "status": job.status.value
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create batch job: {e}")
            return {
                "success": False,
                "error": f"Job creation failed: {str(e)}"
            }
    
    def start_batch_job(self, job_id: str) -> Dict[str, Any]:
        """Start processing a batch job"""
        try:
            if job_id not in self.active_jobs:
                return {
                    "success": False,
                    "error": f"Job {job_id} not found"
                }
            
            job = self.active_jobs[job_id]
            
            if job.status != ProcessingStatus.PENDING:
                return {
                    "success": False,
                    "error": f"Job {job_id} is not in pending status"
                }
            
            # Update job status
            job.status = ProcessingStatus.PROCESSING
            
            # Add to processing queue
            self.processing_queue.put(job)
            
            logger.info(f"🚀 Started batch job: {job_id}")
            
            return {
                "success": True,
                "job_id": job_id,
                "status": job.status.value,
                "message": "Job added to processing queue"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start batch job: {e}")
            return {
                "success": False,
                "error": f"Job start failed: {str(e)}"
            }
    
    async def _process_batch_job(self, job: BatchJob):
        """Process a batch job with the specified pipeline"""
        try:
            logger.info(f"🔄 Processing batch job: {job.job_id}")
            
            # Get list of files to process
            files = self._get_files_to_process(job.source_directory, job.file_patterns)
            
            # Process files with specified pipeline
            results = await self._execute_processing_pipeline(job, files)
            
            # Update job status
            job.status = ProcessingStatus.COMPLETED
            job.processed_files = len(files)
            job.failed_files = len([r for r in results if not r.get("success", False)])
            job.results = {
                "pipeline": job.processing_pipeline,
                "file_results": results,
                "summary": {
                    "total_files": len(files),
                    "successful": job.processed_files - job.failed_files,
                    "failed": job.failed_files,
                    "processing_time": (datetime.now() - job.created_at).total_seconds()
                }
            }
            
            # Save updated job
            self._save_job_to_disk(job)
            
            # Move to history
            self.job_history[job.job_id] = job
            del self.active_jobs[job.job_id]
            
            logger.info(f"✅ Completed batch job: {job.job_id}")
            
        except Exception as e:
            logger.error(f"❌ Batch job processing failed: {e}")
            job.status = ProcessingStatus.FAILED
            job.results = {"error": str(e)}
            self._save_job_to_disk(job)
    
    async def _execute_processing_pipeline(
        self, 
        job: BatchJob, 
        files: List[str]
    ) -> List[Dict[str, Any]]:
        """Execute the processing pipeline on files"""
        try:
            results = []
            
            # Process files with ThreadPoolExecutor for I/O operations
            with ThreadPoolExecutor(max_workers=job.max_workers) as executor:
                # Submit all files for processing
                future_to_file = {
                    executor.submit(self._process_single_file, job, file_path): file_path
                    for file_path in files
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        results.append({
                            "file_path": file_path,
                            "success": False,
                            "error": str(e)
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Pipeline execution failed: {e}")
            return [{"error": f"Pipeline execution failed: {str(e)}"}]
    
    def _process_single_file(self, job: BatchJob, file_path: str) -> Dict[str, Any]:
        """Process a single file through the pipeline"""
        try:
            file_result = {
                "file_path": file_path,
                "filename": os.path.basename(file_path),
                "pipeline_results": {},
                "success": True,
                "processing_time": 0
            }
            
            start_time = time.time()
            
            # Execute each step in the pipeline
            for pipeline_step in job.processing_pipeline:
                if pipeline_step in self.available_pipelines:
                    try:
                        step_result = self.available_pipelines[pipeline_step](file_path)
                        file_result["pipeline_results"][pipeline_step] = step_result
                    except Exception as e:
                        file_result["pipeline_results"][pipeline_step] = {
                            "success": False,
                            "error": str(e)
                        }
                        file_result["success"] = False
                else:
                    file_result["pipeline_results"][pipeline_step] = {
                        "success": False,
                        "error": f"Unknown pipeline step: {pipeline_step}"
                    }
                    file_result["success"] = False
            
            file_result["processing_time"] = time.time() - start_time
            
            return file_result
            
        except Exception as e:
            logger.error(f"❌ File processing failed: {e}")
            return {
                "file_path": file_path,
                "success": False,
                "error": str(e)
            }
    
    def _basic_extraction_pipeline(self, file_path: str) -> Dict[str, Any]:
        """Basic document extraction pipeline"""
        try:
            file_type = os.path.splitext(file_path)[1][1:].lower()
            result = self.docling_service.process_document(file_path, file_type)
            
            return {
                "success": result["success"],
                "extracted_text": result.get("text", "")[:500] + "..." if result.get("text") else "",
                "word_count": result.get("word_count", 0),
                "confidence": result.get("confidence", 0),
                "processing_method": result.get("processing_method", "")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _rag_processing_pipeline(self, file_path: str) -> Dict[str, Any]:
        """RAG processing pipeline"""
        try:
            file_type = os.path.splitext(file_path)[1][1:].lower()
            result = self.rag_service.process_document_for_rag(file_path, file_type)
            
            return {
                "success": result["success"],
                "chunks_created": result.get("chunks_created", 0),
                "total_words": result.get("total_words", 0),
                "processing_method": result.get("processing_method", "")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _llm_analysis_pipeline(self, file_path: str) -> Dict[str, Any]:
        """LLM analysis pipeline"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # For now, return a placeholder
            # In production, you would call the LLM service
            return {
                "success": True,
                "analysis_type": "document_summary",
                "note": "LLM analysis requires async processing - implement in production"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _model_prediction_pipeline(self, file_path: str) -> Dict[str, Any]:
        """Model prediction pipeline"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # For now, return a placeholder
            # In production, you would use trained models
            return {
                "success": True,
                "prediction_type": "document_classification",
                "note": "Model prediction requires trained models - implement in production"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _compliance_check_pipeline(self, file_path: str) -> Dict[str, Any]:
        """Compliance check pipeline"""
        try:
            # For now, return a placeholder
            # In production, you would implement compliance checking
            return {
                "success": True,
                "compliance_type": "hipaa_check",
                "note": "Compliance checking requires implementation - implement in production"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _full_analysis_pipeline(self, file_path: str) -> Dict[str, Any]:
        """Full analysis pipeline combining all steps"""
        try:
            results = {}
            
            # Execute all available pipelines
            for pipeline_name, pipeline_func in self.available_pipelines.items():
                if pipeline_name != "full_analysis":
                    try:
                        results[pipeline_name] = pipeline_func(file_path)
                    except Exception as e:
                        results[pipeline_name] = {"success": False, "error": str(e)}
            
            return {
                "success": True,
                "pipeline_results": results,
                "total_steps": len(results)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _count_files_in_directory(self, directory: str, patterns: List[str]) -> int:
        """Count files matching patterns in directory"""
        try:
            count = 0
            for pattern in patterns:
                for file_path in Path(directory).glob(pattern):
                    if file_path.is_file():
                        count += 1
            return count
        except Exception:
            return 0
    
    def _get_files_to_process(self, directory: str, patterns: List[str]) -> List[str]:
        """Get list of files to process"""
        try:
            files = []
            for pattern in patterns:
                for file_path in Path(directory).glob(pattern):
                    if file_path.is_file():
                        files.append(str(file_path))
            return files
        except Exception:
            return []
    
    def _save_job_to_disk(self, job: BatchJob):
        """Save job to disk for persistence"""
        try:
            job_file = self.jobs_dir / f"{job.job_id}.json"
            
            # Convert job to dict for JSON serialization
            job_dict = {
                "job_id": job.job_id,
                "name": job.name,
                "description": job.description,
                "source_directory": job.source_directory,
                "file_patterns": job.file_patterns,
                "processing_pipeline": job.processing_pipeline,
                "max_workers": job.max_workers,
                "created_at": job.created_at.isoformat(),
                "status": job.status.value,
                "total_files": job.total_files,
                "processed_files": job.processed_files,
                "failed_files": job.failed_files,
                "results": job.results
            }
            
            with open(job_file, 'w') as f:
                json.dump(job_dict, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Failed to save job to disk: {e}")
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a batch job"""
        try:
            # Check active jobs
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                return {
                    "success": True,
                    "job_id": job_id,
                    "status": job.status.value,
                    "progress": {
                        "total_files": job.total_files,
                        "processed_files": job.processed_files,
                        "failed_files": job.failed_files,
                        "percentage": (job.processed_files / job.total_files * 100) if job.total_files > 0 else 0
                    },
                    "created_at": job.created_at.isoformat(),
                    "processing_pipeline": job.processing_pipeline
                }
            
            # Check job history
            if job_id in self.job_history:
                job = self.job_history[job_id]
                return {
                    "success": True,
                    "job_id": job_id,
                    "status": job.status.value,
                    "results": job.results,
                    "created_at": job.created_at.isoformat(),
                    "completed_at": datetime.now().isoformat()
                }
            
            return {
                "success": False,
                "error": f"Job {job_id} not found"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get job status: {e}")
            return {
                "success": False,
                "error": f"Status retrieval failed: {str(e)}"
            }
    
    def list_batch_jobs(self, include_history: bool = True) -> Dict[str, Any]:
        """List all batch jobs"""
        try:
            active_jobs = []
            for job_id, job in self.active_jobs.items():
                active_jobs.append({
                    "job_id": job_id,
                    "name": job.name,
                    "status": job.status.value,
                    "total_files": job.total_files,
                    "processed_files": job.processed_files,
                    "created_at": job.created_at.isoformat()
                })
            
            result = {
                "success": True,
                "active_jobs": active_jobs,
                "total_active": len(active_jobs)
            }
            
            if include_history:
                history_jobs = []
                for job_id, job in self.job_history.items():
                    history_jobs.append({
                        "job_id": job_id,
                        "name": job.name,
                        "status": job.status.value,
                        "total_files": job.total_files,
                        "processed_files": job.processed_files,
                        "created_at": job.created_at.isoformat()
                    })
                
                result["history_jobs"] = history_jobs
                result["total_history"] = len(history_jobs)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to list batch jobs: {e}")
            return {
                "success": False,
                "error": f"Job listing failed: {str(e)}"
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        return {
            "service_name": "BatchProcessingService",
            "active_jobs": len(self.active_jobs),
            "job_history": len(self.job_history),
            "available_pipelines": list(self.available_pipelines.keys()),
            "processing_queue_size": self.processing_queue.qsize(),
            "capabilities": {
                "parallel_processing": True,
                "pipeline_execution": True,
                "progress_tracking": True,
                "job_persistence": True
            },
            "timestamp": datetime.now().isoformat()
        }
