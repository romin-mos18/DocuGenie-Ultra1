"""
AI-Powered Documents API
Complete AI pipeline for document processing, analysis, and labeling
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import logging
from datetime import datetime
from services.ai_document_processor import AIDocumentProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize AI services
ai_processor = AIDocumentProcessor()

# Global document storage (in production, this would be a database)
ai_document_storage = {}
ai_document_counter = 1

@router.post("/ai-upload")
async def upload_document_with_ai(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and process document with complete AI pipeline"""
    global ai_document_counter
    
    try:
        logger.info(f"🤖 Starting AI document upload: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Get file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_type = file_extension[1:]  # Remove the dot
        
        # Check if file type is supported
        supported_types = ['pdf', 'docx', 'doc', 'xlsx', 'xls', 'csv', 'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'txt', 'md', 'rtf']
        if file_type not in supported_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_type}. Supported: {', '.join(supported_types)}"
            )
        
        # Create uploads directory
        upload_dir = "./uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, file.filename)
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"📁 File saved: {file_path}")
        
        # Generate unique document ID
        doc_id = ai_document_counter
        ai_document_counter += 1
        
        # Store initial document metadata
        ai_document_storage[doc_id] = {
            "id": doc_id,
            "filename": file.filename,
            "file_type": file_type,
            "file_path": file_path,
            "file_size": len(content),
            "status": "uploaded",
            "upload_date": datetime.now().isoformat(),
            "ai_processing_result": {},
            "document_type": "unknown",
            "confidence": 0.0
        }
        
        logger.info(f"💾 Document stored with ID: {doc_id}")
        
        # Process with AI immediately
        try:
            logger.info(f"🧠 Starting AI processing for: {file.filename}")
            
            # Update status
            ai_document_storage[doc_id]["status"] = "processing"
            
            # Run AI processing
            ai_result = ai_processor.process_document(file_path, file_type)
            
            if ai_result["success"]:
                # Update storage with AI results
                ai_document_storage[doc_id].update({
                    "status": "processed",
                    "ai_processing_result": ai_result,
                    "document_type": ai_result["classification"]["document_type"],
                    "confidence": ai_result["classification"]["confidence"],
                    "processed_date": datetime.now().isoformat(),
                    "extracted_text": ai_result["extraction"]["text"],
                    "ai_summary": ai_result["summary"]["summary"],
                    "key_information": ai_result["key_information"],
                    "processing_stats": ai_result["processing_stats"]
                })
                
                logger.info(f"✅ AI processing completed: {ai_result['classification']['document_type']} ({ai_result['classification']['confidence']:.1%})")
                
            else:
                # Processing failed
                ai_document_storage[doc_id].update({
                    "status": "error",
                    "ai_processing_result": ai_result,
                    "error": ai_result.get("error", "AI processing failed")
                })
                logger.error(f"❌ AI processing failed: {ai_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ AI processing exception: {e}")
            ai_document_storage[doc_id].update({
                "status": "error",
                "error": str(e)
            })
        
        # Get final document data
        processed_doc = ai_document_storage.get(doc_id, {})
        
        # Format document type for display
        doc_type = processed_doc.get("document_type", "unknown")
        formatted_doc_type = doc_type.replace('_', ' ').title() if doc_type != "unknown" else "Unknown"
        
        return {
            "success": True,
            "message": "Document uploaded and processed with AI!",
            "document_id": doc_id,
            "filename": file.filename,
            "file_type": file_type,
            "file_size": len(content),
            "processing_status": processed_doc.get("status", "uploaded"),
            "document_type": processed_doc.get("document_type", "unknown"),
            "documentType": formatted_doc_type,
            "confidence": processed_doc.get("confidence", 0.0),
            "ai_analysis": {
                "success": processed_doc.get("status") == "processed",
                "document_type": processed_doc.get("document_type", "unknown"),
                "confidence": processed_doc.get("confidence", 0.0),
                "summary": processed_doc.get("ai_summary", ""),
                "processing_method": "ai_powered",
                "extraction_successful": processed_doc.get("ai_processing_result", {}).get("extraction", {}).get("success", False),
                "analysis_successful": processed_doc.get("ai_processing_result", {}).get("analysis", {}).get("success", False)
            },
            "classification": {
                "document_type": processed_doc.get("document_type", "unknown"),
                "confidence": processed_doc.get("confidence", 0.0),
                "success": processed_doc.get("status") == "processed"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ AI document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/ai-documents")
async def get_ai_documents():
    """Get all AI-processed documents"""
    try:
        documents = []
        
        for doc_id, doc_data in ai_document_storage.items():
            # Format document type for display
            doc_type = doc_data.get("document_type", "unknown")
            formatted_doc_type = doc_type.replace('_', ' ').title() if doc_type != "unknown" else "Unknown"
            
            # Get AI processing details
            ai_result = doc_data.get("ai_processing_result", {})
            
            documents.append({
                "id": str(doc_id),
                "filename": doc_data.get("filename", "Unknown"),
                "file_type": doc_data.get("file_type", "unknown"),
                "status": doc_data.get("status", "uploaded"),
                "upload_date": doc_data.get("upload_date", ""),
                "processed_date": doc_data.get("processed_date", ""),
                "file_size": doc_data.get("file_size", 0),
                "document_type": doc_data.get("document_type", "unknown"),
                "documentType": formatted_doc_type,
                "confidence": doc_data.get("confidence", 0.0),
                "ai_summary": doc_data.get("ai_summary", ""),
                "ai_analysis": {
                    "success": doc_data.get("status") == "processed",
                    "document_type": doc_data.get("document_type", "unknown"),
                    "confidence": doc_data.get("confidence", 0.0),
                    "processing_method": "ai_powered",
                    "extraction_successful": ai_result.get("extraction", {}).get("success", False),
                    "analysis_successful": ai_result.get("analysis", {}).get("success", False),
                    "word_count": ai_result.get("extraction", {}).get("word_count", 0),
                    "processing_time": ai_result.get("processing_time", 0)
                },
                "classification": {
                    "document_type": doc_data.get("document_type", "unknown"),
                    "confidence": doc_data.get("confidence", 0.0),
                    "success": doc_data.get("status") == "processed",
                    "reasoning": ai_result.get("classification", {}).get("reasoning", []),
                    "alternatives": ai_result.get("classification", {}).get("alternatives", [])
                },
                "key_information": doc_data.get("key_information", {}),
                "processing_stats": doc_data.get("processing_stats", {})
            })
        
        logger.info(f"📚 Retrieved {len(documents)} AI-processed documents")
        return {"documents": documents, "total": len(documents)}
        
    except Exception as e:
        logger.error(f"Error fetching AI documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

@router.get("/ai-documents/{document_id}")
async def get_ai_document_details(document_id: str):
    """Get detailed AI analysis for a specific document"""
    try:
        doc_id = int(document_id)
        
        if doc_id not in ai_document_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = ai_document_storage[doc_id]
        ai_result = doc_data.get("ai_processing_result", {})
        
        # Format document type
        doc_type = doc_data.get("document_type", "unknown")
        formatted_doc_type = doc_type.replace('_', ' ').title() if doc_type != "unknown" else "Unknown"
        
        return {
            "success": True,
            "document": {
                "id": str(doc_id),
                "filename": doc_data.get("filename", "Unknown"),
                "file_type": doc_data.get("file_type", "unknown"),
                "status": doc_data.get("status", "uploaded"),
                "upload_date": doc_data.get("upload_date", ""),
                "processed_date": doc_data.get("processed_date", ""),
                "file_size": doc_data.get("file_size", 0),
                "document_type": doc_data.get("document_type", "unknown"),
                "documentType": formatted_doc_type,
                "confidence": doc_data.get("confidence", 0.0)
            },
            "ai_analysis": {
                "success": doc_data.get("status") == "processed",
                "processing_method": "ai_powered",
                "processing_time": ai_result.get("processing_time", 0),
                
                # Extraction Results
                "extraction": ai_result.get("extraction", {}),
                
                # Content Analysis
                "content_analysis": ai_result.get("analysis", {}).get("content_analysis", {}),
                "structural_analysis": ai_result.get("analysis", {}).get("structural_analysis", {}),
                "semantic_analysis": ai_result.get("analysis", {}).get("semantic_analysis", {}),
                
                # Classification Results
                "classification": ai_result.get("classification", {}),
                
                # Summary and Key Information
                "summary": ai_result.get("summary", {}),
                "key_information": ai_result.get("key_information", {}),
                
                # Processing Statistics
                "processing_stats": ai_result.get("processing_stats", {})
            },
            "extracted_text": doc_data.get("extracted_text", ""),
            "ai_summary": doc_data.get("ai_summary", "")
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        logger.error(f"❌ Failed to fetch AI document details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch document: {str(e)}")

@router.delete("/ai-documents/{document_id}")
async def delete_ai_document(document_id: str):
    """Delete an AI-processed document"""
    try:
        doc_id = int(document_id)
        
        if doc_id not in ai_document_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = ai_document_storage[doc_id]
        file_path = doc_data.get("file_path")
        
        # Remove file if it exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"🗑️ Deleted file: {file_path}")
            except Exception as e:
                logger.warning(f"⚠️ Could not delete file {file_path}: {e}")
        
        # Remove from storage
        del ai_document_storage[doc_id]
        
        logger.info(f"✅ AI document {doc_id} deleted successfully")
        
        return {
            "success": True,
            "message": "AI document deleted successfully",
            "document_id": document_id,
            "deleted_at": datetime.now().isoformat()
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        logger.error(f"❌ Failed to delete AI document: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.get("/ai-stats")
async def get_ai_processing_stats():
    """Get AI processing statistics"""
    try:
        # Get processor stats
        processor_stats = ai_processor.get_processing_stats()
        
        # Calculate document stats
        total_docs = len(ai_document_storage)
        processed_docs = len([doc for doc in ai_document_storage.values() if doc.get("status") == "processed"])
        processing_docs = len([doc for doc in ai_document_storage.values() if doc.get("status") == "processing"])
        failed_docs = len([doc for doc in ai_document_storage.values() if doc.get("status") == "error"])
        
        # Document type distribution
        doc_types = {}
        for doc in ai_document_storage.values():
            doc_type = doc.get("document_type", "unknown")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        # Average confidence
        confidences = [doc.get("confidence", 0.0) for doc in ai_document_storage.values() if doc.get("confidence", 0.0) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "success": True,
            "ai_processing_stats": {
                "processor_stats": processor_stats,
                "document_stats": {
                    "total_documents": total_docs,
                    "processed_successfully": processed_docs,
                    "currently_processing": processing_docs,
                    "failed_processing": failed_docs,
                    "success_rate": (processed_docs / total_docs * 100) if total_docs > 0 else 0
                },
                "classification_stats": {
                    "document_type_distribution": doc_types,
                    "average_confidence": avg_confidence,
                    "high_confidence_docs": len([c for c in confidences if c > 0.8]),
                    "low_confidence_docs": len([c for c in confidences if c < 0.5])
                },
                "capabilities": processor_stats["capabilities"],
                "supported_types": processor_stats["supported_types"]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch AI stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats fetch failed: {str(e)}")

@router.post("/ai-documents/{document_id}/reprocess")
async def reprocess_ai_document(document_id: str):
    """Reprocess a document with AI"""
    try:
        doc_id = int(document_id)
        
        if doc_id not in ai_document_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = ai_document_storage[doc_id]
        file_path = doc_data.get("file_path")
        file_type = doc_data.get("file_type")
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document file not found")
        
        logger.info(f"🔄 Reprocessing document {doc_id} with AI")
        
        # Update status
        ai_document_storage[doc_id]["status"] = "processing"
        
        # Reprocess with AI
        ai_result = ai_processor.process_document(file_path, file_type)
        
        if ai_result["success"]:
            # Update storage with new AI results
            ai_document_storage[doc_id].update({
                "status": "processed",
                "ai_processing_result": ai_result,
                "document_type": ai_result["classification"]["document_type"],
                "confidence": ai_result["classification"]["confidence"],
                "processed_date": datetime.now().isoformat(),
                "extracted_text": ai_result["extraction"]["text"],
                "ai_summary": ai_result["summary"]["summary"],
                "key_information": ai_result["key_information"],
                "processing_stats": ai_result["processing_stats"]
            })
            
            logger.info(f"✅ AI reprocessing completed: {ai_result['classification']['document_type']} ({ai_result['classification']['confidence']:.1%})")
            
            return {
                "success": True,
                "message": "Document reprocessed successfully with AI",
                "document_id": document_id,
                "document_type": ai_result["classification"]["document_type"],
                "confidence": ai_result["classification"]["confidence"],
                "processing_time": ai_result["processing_time"]
            }
        else:
            ai_document_storage[doc_id].update({
                "status": "error",
                "error": ai_result.get("error", "AI reprocessing failed")
            })
            
            raise HTTPException(status_code=500, detail=f"AI reprocessing failed: {ai_result.get('error', 'Unknown error')}")
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        logger.error(f"❌ AI reprocessing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")
