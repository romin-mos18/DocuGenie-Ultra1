"""
Enhanced Features API Router
Phase 3: Search, Workflow, and Compliance Services
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import logging

# Import services
from services.search_service import SearchService
from services.workflow_service import WorkflowService
from services.compliance_service import ComplianceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enhanced", tags=["Enhanced Features"])

# Initialize services
search_service = SearchService()
workflow_service = WorkflowService()
compliance_service = ComplianceService()

# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str
    search_type: str = "hybrid"
    filters: Optional[Dict[str, Any]] = None
    limit: int = 20

class WorkflowCreateRequest(BaseModel):
    document_id: str
    workflow_type: str
    assignees: Dict[str, str]
    metadata: Optional[Dict[str, Any]] = None

class WorkflowStepRequest(BaseModel):
    action: str
    user_id: str
    comments: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ComplianceCheckRequest(BaseModel):
    document_id: str
    document_content: str
    compliance_types: Optional[List[str]] = None

# Search Endpoints
@router.get("/search/status")
async def get_search_status():
    """Get search service status and capabilities"""
    try:
        status = search_service.get_service_status()
        return {
            "success": True,
            "search_service": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting search status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/documents")
async def search_documents(request: SearchRequest):
    """Search documents using available search engines"""
    try:
        results = search_service.search_documents(
            query=request.query,
            search_type=request.search_type,
            filters=request.filters or {},
            limit=request.limit
        )
        return {
            "success": True,
            "search_results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/analytics")
async def get_search_analytics():
    """Get search analytics and performance metrics"""
    try:
        analytics = search_service.get_search_analytics()
        return {
            "success": True,
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting search analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Workflow Endpoints
@router.get("/workflow/status")
async def get_workflow_status():
    """Get workflow service status and capabilities"""
    try:
        status = workflow_service.get_service_status()
        return {
            "success": True,
            "workflow_service": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/create")
async def create_workflow(request: WorkflowCreateRequest):
    """Create a new workflow for document processing"""
    try:
        result = workflow_service.create_workflow(
            document_id=request.document_id,
            workflow_type=request.workflow_type,
            assignees=request.assignees,
            metadata=request.metadata or {}
        )
        return {
            "success": True,
            "workflow": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/{workflow_id}/start")
async def start_workflow(workflow_id: str, user_id: str = Query(...)):
    """Start a workflow"""
    try:
        result = workflow_service.start_workflow(workflow_id, user_id)
        return {
            "success": True,
            "workflow_started": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/{workflow_id}/status")
async def get_workflow_status_by_id(workflow_id: str):
    """Get status of a specific workflow"""
    try:
        result = workflow_service.get_workflow_status(workflow_id)
        return {
            "success": True,
            "workflow_status": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/{workflow_id}/step/{step_id}")
async def process_workflow_step(
    workflow_id: str, 
    step_id: str, 
    request: WorkflowStepRequest
):
    """Process a workflow step (approve, reject, request changes)"""
    try:
        result = workflow_service.process_workflow_step(
            workflow_id=workflow_id,
            step_id=step_id,
            action=request.action,
            user_id=request.user_id,
            comments=request.comments or "",
            metadata=request.metadata or {}
        )
        return {
            "success": True,
            "step_processed": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing workflow step: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/list")
async def list_workflows(limit: int = Query(10, ge=1, le=100)):
    """List workflows with optional filtering"""
    try:
        result = workflow_service.list_workflows(limit=limit)
        return {
            "success": True,
            "workflows": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/analytics")
async def get_workflow_analytics():
    """Get workflow analytics and performance metrics"""
    try:
        analytics = workflow_service.get_workflow_analytics()
        return {
            "success": True,
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting workflow analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Compliance Endpoints
@router.get("/compliance/status")
async def get_compliance_status():
    """Get compliance service status and capabilities"""
    try:
        status = compliance_service.get_service_status()
        return {
            "success": True,
            "compliance_service": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting compliance status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compliance/check")
async def check_document_compliance(request: ComplianceCheckRequest):
    """Check document for compliance with various regulations"""
    try:
        # Create mock document data for compliance check
        document_data = {
            "id": request.document_id,
            "extracted_text": request.document_content,
            "filename": f"document_{request.document_id}.pdf"
        }
        
        result = compliance_service.check_document_compliance(document_data)
        return {
            "success": True,
            "compliance_check": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/analytics")
async def get_compliance_analytics():
    """Get compliance analytics and risk metrics"""
    try:
        analytics = compliance_service.get_compliance_analytics()
        return {
            "success": True,
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting compliance analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Features Overview
@router.get("/overview")
async def get_enhanced_features_overview():
    """Get overview of all enhanced features and their status"""
    try:
        # Get status from all services
        search_status = search_service.get_service_status()
        workflow_status = workflow_service.get_service_status()
        compliance_status = compliance_service.get_service_status()
        
        return {
            "success": True,
            "enhanced_features": {
                "search": {
                    "status": "active",
                    "capabilities": search_status.get("search_capabilities", {}),
                    "engines": search_status.get("search_engines", {}),
                    "analytics": search_status.get("analytics", {})
                },
                "workflow": {
                    "status": "active",
                    "capabilities": workflow_status.get("capabilities", {}),
                    "templates": workflow_status.get("workflow_templates", []),
                    "total_workflows": workflow_status.get("total_workflows", 0)
                },
                "compliance": {
                    "status": "active",
                    "capabilities": compliance_status.get("capabilities", {}),
                    "compliance_types": compliance_status.get("compliance_types", []),
                    "total_audit_entries": compliance_status.get("total_audit_entries", 0)
                }
            },
            "phase": "Phase 3 - Enhanced Features",
            "status": "fully_operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting enhanced features overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
