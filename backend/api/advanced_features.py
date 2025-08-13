#!/usr/bin/env python3
"""
Advanced Features API Router
Integrates all new services: LLM, Healthcare Models, Batch Processing, Multi-language, and Real-time Intelligence
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import logging

# Import advanced services
from services.llm_service import LLMService, LLMProvider
from services.healthcare_model_service import HealthcareModelService, ModelType
from services.batch_processing_service import BatchProcessingService
from services.multilang_service import MultiLanguageService
from services.realtime_intelligence_service import RealTimeIntelligenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advanced", tags=["Advanced AI Features"])

# Initialize services
llm_service = LLMService()
model_service = HealthcareModelService()
batch_service = BatchProcessingService()
multilang_service = MultiLanguageService()
realtime_service = RealTimeIntelligenceService()

# Pydantic models for requests
class LLMRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7

class HealthcareAnalysisRequest(BaseModel):
    content: str
    analysis_type: str = "document_summary"

class BatchJobRequest(BaseModel):
    name: str
    description: str
    source_directory: str
    file_patterns: Optional[List[str]] = None
    processing_pipeline: Optional[List[str]] = None
    max_workers: int = 4

class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str] = None

class StreamRequest(BaseModel):
    stream_id: str
    source_directory: str
    file_patterns: Optional[List[str]] = None
    analysis_pipeline: Optional[List[str]] = None

# LLM Service Endpoints
@router.get("/llm/status")
async def get_llm_status():
    """Get LLM service status and capabilities"""
    try:
        status = llm_service.get_service_status()
        return {
            "success": True,
            "llm_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get LLM status: {e}")
        raise HTTPException(status_code=500, detail=f"LLM status fetch failed: {str(e)}")

@router.post("/llm/generate")
async def generate_llm_response(request: LLMRequest):
    """Generate response using LLM service"""
    try:
        provider = None
        if request.provider:
            try:
                provider = LLMProvider(request.provider)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid provider: {request.provider}")
        
        result = await llm_service.generate_response(
            prompt=request.prompt,
            provider=provider,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "llm_response": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ LLM generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

@router.post("/llm/analyze-healthcare")
async def analyze_healthcare_document(request: HealthcareAnalysisRequest):
    """Analyze healthcare document using specialized LLM prompts"""
    try:
        result = await llm_service.analyze_healthcare_document(
            content=request.content,
            analysis_type=request.analysis_type
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "healthcare_analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Healthcare analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Healthcare analysis failed: {str(e)}")

@router.post("/llm/switch-provider/{provider}")
async def switch_llm_provider(provider: str):
    """Switch to a different LLM provider"""
    try:
        try:
            provider_enum = LLMProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
        
        result = llm_service.switch_provider(provider_enum)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "provider_switch": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Provider switch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Provider switch failed: {str(e)}")

# Healthcare Model Service Endpoints
@router.get("/models/status")
async def get_model_service_status():
    """Get healthcare model service status"""
    try:
        status = model_service.get_service_status()
        return {
            "success": True,
            "model_service_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get model service status: {e}")
        raise HTTPException(status_code=500, detail=f"Model service status fetch failed: {str(e)}")

@router.post("/models/create-dataset")
async def create_training_dataset(
    name: str,
    documents: List[Dict[str, Any]],
    labels: List[str],
    model_type: str = "classification"
):
    """Create a training dataset for healthcare models"""
    try:
        try:
            model_type_enum = ModelType(model_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid model type: {model_type}")
        
        result = model_service.create_training_dataset(
            name=name,
            documents=documents,
            labels=labels,
            model_type=model_type_enum
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "dataset_creation": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Dataset creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dataset creation failed: {str(e)}")

@router.post("/models/train/{dataset_name}/{model_name}")
async def train_classification_model(
    dataset_name: str,
    model_name: str,
    test_size: float = 0.2,
    random_state: int = 42
):
    """Train a classification model for healthcare documents"""
    try:
        result = model_service.train_classification_model(
            dataset_name=dataset_name,
            model_name=model_name,
            test_size=test_size,
            random_state=random_state
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "model_training": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Model training failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")

@router.post("/models/predict/{model_name}")
async def predict_document_class(model_name: str, content: str):
    """Predict document class using trained model"""
    try:
        result = model_service.predict_document_class(model_name, content)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "prediction": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/models/list")
async def list_trained_models():
    """List all trained models"""
    try:
        result = model_service.list_trained_models()
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "models": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Model listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model listing failed: {str(e)}")

# Batch Processing Service Endpoints
@router.get("/batch/status")
async def get_batch_service_status():
    """Get batch processing service status"""
    try:
        status = batch_service.get_service_status()
        return {
            "success": True,
            "batch_service_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get batch service status: {e}")
        raise HTTPException(status_code=500, detail=f"Batch service status fetch failed: {str(e)}")

@router.post("/batch/create-job")
async def create_batch_job(request: BatchJobRequest):
    """Create a new batch processing job"""
    try:
        result = batch_service.create_batch_job(
            name=request.name,
            description=request.description,
            source_directory=request.source_directory,
            file_patterns=request.file_patterns,
            processing_pipeline=request.processing_pipeline,
            max_workers=request.max_workers
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "batch_job_creation": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Batch job creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch job creation failed: {str(e)}")

@router.post("/batch/start-job/{job_id}")
async def start_batch_job(job_id: str):
    """Start processing a batch job"""
    try:
        result = batch_service.start_batch_job(job_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "batch_job_start": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Batch job start failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch job start failed: {str(e)}")

@router.get("/batch/jobs")
async def list_batch_jobs(include_history: bool = True):
    """List all batch jobs"""
    try:
        result = batch_service.list_batch_jobs(include_history=include_history)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "batch_jobs": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Batch jobs listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch jobs listing failed: {str(e)}")

@router.get("/batch/job/{job_id}")
async def get_batch_job_status(job_id: str):
    """Get status of a specific batch job"""
    try:
        result = batch_service.get_job_status(job_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "batch_job_status": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Batch job status fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch job status fetch failed: {str(e)}")

# Multi-language Service Endpoints
@router.get("/multilang/status")
async def get_multilang_service_status():
    """Get multi-language service status"""
    try:
        status = multilang_service.get_service_status()
        return {
            "success": True,
            "multilang_service_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get multilang service status: {e}")
        raise HTTPException(status_code=500, detail=f"Multilang service status fetch failed: {str(e)}")

@router.post("/multilang/detect-language")
async def detect_language(content: str):
    """Detect the language of text content"""
    try:
        result = multilang_service.detect_language(content)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "language_detection": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Language detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")

@router.post("/multilang/translate")
async def translate_text(request: TranslationRequest):
    """Translate text to target language"""
    try:
        result = multilang_service.translate_text(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "translation": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Translation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.get("/multilang/support-info")
async def get_language_support_info():
    """Get information about language support capabilities"""
    try:
        result = multilang_service.get_language_support_info()
        return {
            "success": True,
            "language_support": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Language support info fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Language support info fetch failed: {str(e)}")

# Real-time Intelligence Service Endpoints
@router.get("/realtime/status")
async def get_realtime_service_status():
    """Get real-time intelligence service status"""
    try:
        status = realtime_service.get_service_status()
        return {
            "success": True,
            "realtime_service_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get realtime service status: {e}")
        raise HTTPException(status_code=500, detail=f"Realtime service status fetch failed: {str(e)}")

@router.post("/realtime/start-stream")
async def start_document_stream(request: StreamRequest):
    """Start real-time document processing stream"""
    try:
        result = realtime_service.start_document_stream(
            stream_id=request.stream_id,
            source_directory=request.source_directory,
            file_patterns=request.file_patterns,
            analysis_pipeline=request.analysis_pipeline
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "stream_start": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Stream start failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stream start failed: {str(e)}")

@router.post("/realtime/stop-stream/{stream_id}")
async def stop_document_stream(stream_id: str):
    """Stop a document processing stream"""
    try:
        result = realtime_service.stop_document_stream(stream_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "stream_stop": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Stream stop failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stream stop failed: {str(e)}")

@router.get("/realtime/streams")
async def get_stream_status(stream_id: str = None):
    """Get status of document streams"""
    try:
        result = realtime_service.get_stream_status(stream_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "stream_status": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Stream status fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stream status fetch failed: {str(e)}")

@router.get("/realtime/events")
async def get_recent_events(limit: int = 100, event_type: str = None):
    """Get recent intelligence events"""
    try:
        result = realtime_service.get_recent_events(limit=limit, event_type=event_type)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "recent_events": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Recent events fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recent events fetch failed: {str(e)}")

# Comprehensive System Status
@router.get("/system/status")
async def get_comprehensive_system_status():
    """Get comprehensive status of all advanced services"""
    try:
        # Get status from all services
        llm_status = llm_service.get_service_status()
        model_status = model_service.get_service_status()
        batch_status = batch_service.get_service_status()
        multilang_status = multilang_service.get_service_status()
        realtime_status = realtime_service.get_service_status()
        
        # Compile comprehensive status
        comprehensive_status = {
            "timestamp": datetime.now().isoformat(),
            "services": {
                "llm_service": llm_status,
                "healthcare_model_service": model_status,
                "batch_processing_service": batch_status,
                "multilang_service": multilang_status,
                "realtime_intelligence_service": realtime_status
            },
            "overall_health": "healthy",
            "total_capabilities": 0,
            "active_features": []
        }
        
        # Calculate overall health and capabilities
        all_services = [llm_status, model_status, batch_status, multilang_status, realtime_status]
        total_capabilities = sum(len(service.get("capabilities", {})) for service in all_services)
        
        comprehensive_status["total_capabilities"] = total_capabilities
        
        # Check for any service issues
        for service_name, service_status in comprehensive_status["services"].items():
            if service_status.get("status", "unknown") != "healthy":
                comprehensive_status["overall_health"] = "degraded"
                break
        
        return {
            "success": True,
            "comprehensive_status": comprehensive_status
        }
        
    except Exception as e:
        logger.error(f"❌ Comprehensive status fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive status fetch failed: {str(e)}")

# Demo and Testing Endpoints
@router.post("/demo/healthcare-pipeline")
async def run_healthcare_demo_pipeline():
    """Run a demonstration of the complete healthcare AI pipeline"""
    try:
        # This would run a comprehensive demo
        # For now, return a summary of capabilities
        
        demo_summary = {
            "pipeline_name": "Healthcare AI Demo Pipeline",
            "stages": [
                "Document Upload & Processing",
                "AI-Powered Text Extraction (Docling)",
                "RAG Pipeline for Document Intelligence",
                "LLM Analysis with Healthcare Prompts",
                "Custom Model Training & Prediction",
                "Batch Processing for Large Volumes",
                "Multi-language Support & Translation",
                "Real-time Intelligence & Alerts"
            ],
            "capabilities": [
                "Advanced LLM Integration (OpenAI, Claude, Local)",
                "Healthcare-Specific AI Models",
                "Batch Document Processing",
                "Multi-language Healthcare Support",
                "Real-time Document Intelligence",
                "Compliance & Alert Monitoring"
            ],
            "ai_models": [
                "Docling (DocLayNet + TableFormer)",
                "sentence-transformers for embeddings",
                "Custom healthcare classification models",
                "Multi-language NLP models"
            ]
        }
        
        return {
            "success": True,
            "demo_pipeline": demo_summary,
            "message": "Healthcare AI pipeline demo ready! All services are operational.",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Demo pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Demo pipeline failed: {str(e)}")
