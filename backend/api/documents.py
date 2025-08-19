"""
Documents API with working AI integration
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import logging
from datetime import datetime
from database.session import get_db
from sqlalchemy.orm import Session

# Import AI services
from services.docling_service import DoclingService
from services.classification_service import DocumentClassificationService  
from services.multilang_service import MultiLanguageService
from services.structured_data_service import StructuredDataService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
docling_service = DoclingService()
classification_service = DocumentClassificationService()
multilang_service = MultiLanguageService()
structured_data_service = StructuredDataService()

# Global document storage (in production, this would be a database)
document_storage = {}
document_counter = 1

@router.get("/")
async def get_documents(db: Session = Depends(get_db)):
    """Get all documents from storage"""
    try:
        # Return actual documents from storage instead of hardcoded data
        documents = []
        
        for doc_id, doc_data in document_storage.items():
            # Format document type for display
            doc_type = doc_data.get("document_type", "unknown")
            formatted_doc_type = doc_type.replace('_', ' ').title() if doc_type != "unknown" else "Unknown"
            
            # Get AI analysis data
            ai_analysis = doc_data.get("ai_analysis", {})
            entity_count = ai_analysis.get("entity_count", 0)
            extracted_entities = ai_analysis.get("extracted_entities_list", {})
            
            documents.append({
                "id": str(doc_id),
                "filename": doc_data.get("filename", "Unknown"),
                "file_type": doc_data.get("file_type", "unknown"),
                "status": doc_data.get("status", "uploaded"),
                "upload_date": doc_data.get("upload_date", ""),
                "file_size": doc_data.get("file_size", 0),
                "ai_analysis": {
                    **ai_analysis,
                    "entity_count": entity_count,
                    "extracted_entities": extracted_entities,
                    "has_entities": entity_count > 0
                },
                "docling_result": doc_data.get("docling_result", {}),
                "extracted_entities": doc_data.get("extracted_entities", {}),
                "document_type": doc_data.get("document_type", "unknown"),
                "documentType": formatted_doc_type,
                "confidence": doc_data.get("confidence", 0.0),
                "classification": {
                    "document_type": doc_data.get("document_type", "unknown"),
                    "confidence": doc_data.get("confidence", 0.0),
                    "success": doc_data.get("status") == "processed",
                    "entity_count": entity_count,
                    "processing_method": ai_analysis.get("processing_method", "unknown")
                }
            })
        
        logger.info(f"📚 Retrieved {len(documents)} documents from storage")
        return {"documents": documents, "total": len(documents)}
        
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        return {"documents": [], "total": 0}

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process document with AI classification"""
    global document_counter
    
    try:
        logger.info(f"🔄 Starting document upload: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Get file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_type = file_extension[1:]  # Remove the dot
        
        # Check if file type is supported
        supported_types = [
            'pdf', 'docx', 'doc', 'xlsx', 'xls', 'csv', 'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif', 'webp',
            'txt', 'md', 'rtf', 'json', 'xml', 'html', 'htm', 'css', 'js', 'zip', 'rar', '7z'
        ]
        if file_type not in supported_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_type}. Supported: {', '.join(supported_types)}"
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = "./uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, file.filename)
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"📁 File saved: {file_path}")
        
        # Generate unique document ID
        doc_id = document_counter
        document_counter += 1
        
        # Store document metadata
        document_storage[doc_id] = {
            "id": doc_id,
            "filename": file.filename,
            "file_type": file_type,
            "file_path": file_path,
            "file_size": len(content),
            "status": "uploaded",
            "upload_date": datetime.now().isoformat(),
            "ai_analysis": {},
            "docling_result": {},
            "extracted_entities": {},
            "document_type": "unknown",
            "confidence": 0.0
        }
        
        logger.info(f"💾 Document stored with ID: {doc_id}")
        
        # Process document with AI classification immediately 
        try:
            logger.info(f"🤖 Starting AI classification for: {file.filename}")
            
            # Update status to processing
            document_storage[doc_id]["status"] = "processing"
            
            # Process with DocLing
            docling_result = docling_service.process_document(file_path, file_type)
            
            # Extract structured data for structured file types (independent of DocLing)
            structured_data_result = None
            if file_type in ['csv', 'json', 'xml', 'xlsx', 'xls']:
                try:
                    logger.info(f"📊 Extracting structured data from {file_type.upper()} file")
                    structured_data_result = structured_data_service.extract_structured_data(file_path, file_type, content)
                    logger.info(f"✅ Structured data extraction: {structured_data_result.get('success', False)}")
                except Exception as struct_error:
                    logger.warning(f"⚠️ Structured data extraction failed: {struct_error}")
                    structured_data_result = {"success": False, "error": str(struct_error)}
            
            # Determine extracted text source
            extracted_text = ""
            
            if docling_result["success"]:
                # Use DocLing text extraction
                extracted_text = docling_result["text"]
                logger.info(f"✅ DocLing text extraction: {len(extracted_text)} characters")
            elif structured_data_result and structured_data_result.get("success"):
                # Fallback: Create text from structured data when DocLing fails
                logger.info(f"🔄 DocLing failed for {file_type}, using structured data as text source")
                structured_data = structured_data_result.get("structured_data", {})
                
                # Create descriptive text from structured data
                if "headers" in structured_data and "rows" in structured_data:
                    # CSV/Excel style data
                    extracted_text = f"This is a {file_type.upper()} file with structured data.\n"
                    extracted_text += f"Columns: {', '.join(structured_data['headers'])}\n"
                    extracted_text += f"Total Rows: {structured_data.get('total_rows', 0)}\n\n"
                    
                    # Add sample data rows for classification
                    rows = structured_data.get("rows", [])
                    for i, row in enumerate(rows[:5]):  # First 5 rows
                        row_text = ", ".join([f"{k}: {v}" for k, v in row.items() if v])
                        extracted_text += f"Row {i+1}: {row_text}\n"
                        
                elif "key_info" in structured_data:
                    # JSON/XML style data
                    extracted_text = f"This is a {file_type.upper()} file with key-value data.\n"
                    key_info = structured_data["key_info"]
                    for key, value in key_info.items():
                        if value:
                            extracted_text += f"{key.replace('_', ' ').title()}: {value}\n"
                
                logger.info(f"✅ Generated text from structured data: {len(extracted_text)} characters")
            else:
                logger.error(f"❌ Both DocLing and structured data extraction failed for {file_type}")
                document_storage[doc_id]["status"] = "error"
            
            # Enhance extracted text with structured data summary
            if structured_data_result and structured_data_result.get("success"):
                structured_summary = f"\n\nStructured Data Summary:\n"
                structured_summary += f"Data Type: {structured_data_result.get('data_type', 'unknown')}\n"
                
                structured_data = structured_data_result.get("structured_data", {})
                if "headers" in structured_data:
                    structured_summary += f"Columns: {', '.join(structured_data['headers'][:5])}\n"
                    structured_summary += f"Total Rows: {structured_data.get('total_rows', 0)}\n"
                elif "key_info" in structured_data:
                    key_info = structured_data["key_info"]
                    for key, value in key_info.items():
                        if value:
                            structured_summary += f"{key.replace('_', ' ').title()}: {value}\n"
                
                extracted_text += structured_summary
            
            # Proceed with AI processing if we have text
            if extracted_text:
                # Classify document (now with enhanced text including structured data info)
                classification_result = classification_service.classify_document(extracted_text)
                
                # Extract entities (safe call with error handling)
                try:
                    logger.info(f"🔍 Starting entity extraction from {len(extracted_text)} characters of text")
                    entities_result = classification_service.extract_entities(extracted_text)
                    logger.info(f"✅ Entity extraction completed: {entities_result.get('success', False)}")
                    logger.info(f"📊 Entities found: {entities_result.get('entity_count', 0)}")
                    if entities_result.get('entity_count', 0) == 0:
                        logger.warning(f"⚠️ Entity extraction returned 0 entities for content: {extracted_text[:200]}...")
                except Exception as entity_error:
                    logger.error(f"❌ Entity extraction failed with error: {entity_error}")
                    import traceback
                    traceback.print_exc()
                    entities_result = {"success": False, "entities": {}, "entity_count": 0}
                
                # Detect language (safe call with error handling)
                try:
                    lang_result = multilang_service.detect_language(extracted_text)
                except Exception as lang_error:
                    logger.warning(f"⚠️ Language detection failed, using default: {lang_error}")
                    lang_result = {"primary_language": "en", "confidence": 0.5, "detected_languages": []}
                
                # Update document storage with results
                ai_analysis = {
                    "classification": classification_result,
                    "entities": entities_result,
                    "language": lang_result,
                    "processing_timestamp": datetime.now().isoformat(),
                    "text_preview": extracted_text[:300] + "..." if len(extracted_text) > 300 else extracted_text,
                    "word_count": len(extracted_text.split()),
                    "entity_count": entities_result.get("entity_count", 0),
                    "extracted_entities_list": entities_result.get("entities", {}),
                    "processing_method": "content_analysis"
                }
                
                # Add structured data if available
                if structured_data_result and structured_data_result.get("success"):
                    ai_analysis["structured_data"] = structured_data_result
                    ai_analysis["has_structured_data"] = True
                    ai_analysis["data_type"] = structured_data_result.get("data_type", "unknown")
                    
                    # Add test results for medical/lab documents
                    structured_data = structured_data_result.get("structured_data", {})
                    if structured_data_result.get("data_type") in ["lab_result", "medical_report"] and "rows" in structured_data:
                        test_results = []
                        for row in structured_data["rows"][:10]:  # Limit to 10 test results
                            test_results.append({
                                "name": row.get("test_name", "Unknown Test"),
                                "value": row.get("value", "N/A"),
                                "unit": row.get("unit", ""),
                                "reference": row.get("reference_range", "N/A"),
                                "flag": row.get("flag", "Normal")
                            })
                        ai_analysis["test_results"] = test_results
                else:
                    ai_analysis["has_structured_data"] = False
                
                document_storage[doc_id].update({
                    "docling_result": docling_result,
                    "extracted_entities": entities_result,
                    "structured_data_result": structured_data_result,
                    "document_type": classification_result.get("document_type", "unknown"),
                    "confidence": classification_result.get("confidence", 0.0),
                    "ai_analysis": ai_analysis,
                    "status": "processed"
                })
                
                logger.info(f"✅ AI processing completed for document: {doc_id}")
                logger.info(f"   Document Type: {classification_result.get('document_type', 'unknown')}")
                logger.info(f"   Confidence: {classification_result.get('confidence', 0.0):.1%}")
                logger.info(f"   Entities Extracted: {entities_result.get('entity_count', 0)}")
                logger.info(f"   Text Length: {len(extracted_text)} characters")
            else:
                logger.error(f"❌ No text extracted - cannot proceed with AI processing")
                document_storage[doc_id]["status"] = "error"
                
        except Exception as e:
            logger.error(f"❌ AI processing failed: {e}")
            document_storage[doc_id]["status"] = "error"
        
        # Get final document data
        processed_doc = document_storage.get(doc_id, {})
        
        return {
            "success": True,
            "message": "Document uploaded and processed successfully with AI classification!",
            "document_id": doc_id,
            "filename": file.filename,
            "file_type": file_type,
            "file_size": len(content),
            "processing_status": "completed" if processed_doc.get("status") == "processed" else "queued",
            "document_type": processed_doc.get("document_type", "unknown"),
            "confidence": processed_doc.get("confidence", 0.0),
            "ai_analysis": processed_doc.get("ai_analysis", {}),
            "classification": {
                "document_type": processed_doc.get("document_type", "unknown"),
                "confidence": processed_doc.get("confidence", 0.0),
                "success": processed_doc.get("status") == "processed"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document"""
    try:
        doc_id = int(document_id)
        
        if doc_id not in document_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Remove file if it exists
        doc_data = document_storage[doc_id]
        file_path = doc_data.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"⚠️ Could not delete file {file_path}: {e}")
        
        # Remove from storage
        del document_storage[doc_id]
        
        logger.info(f"✅ Document {doc_id} deleted successfully")
        
        return {
            "success": True,
            "message": "Document deleted successfully",
            "document_id": document_id,
            "deleted_at": datetime.now().isoformat()
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        logger.error(f"❌ Delete failed: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
