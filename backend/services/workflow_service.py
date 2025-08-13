"""
Workflow Management Service
Manages document approval, review, and workflow processes
"""
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
from enum import Enum

from core.config import settings

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow status enumeration"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CHANGES = "requires_changes"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class WorkflowType(Enum):
    """Workflow type enumeration"""
    DOCUMENT_APPROVAL = "document_approval"
    MEDICAL_REVIEW = "medical_review"
    COMPLIANCE_CHECK = "compliance_check"
    QUALITY_ASSURANCE = "quality_assurance"
    CLINICAL_VALIDATION = "clinical_validation"
    REGULATORY_SUBMISSION = "regulatory_submission"

class WorkflowStep(Enum):
    """Workflow step enumeration"""
    INITIAL_REVIEW = "initial_review"
    MEDICAL_REVIEW = "medical_review"
    COMPLIANCE_CHECK = "compliance_check"
    QUALITY_ASSURANCE = "quality_assurance"
    FINAL_APPROVAL = "final_approval"
    COMPLETION = "completion"

class WorkflowService:
    """Workflow management service for document processing"""
    
    def __init__(self):
        """Initialize workflow service"""
        self.workflows = {}  # In-memory storage for now
        self.workflow_templates = self._initialize_workflow_templates()
        self.notification_callbacks = []
        
        logger.info("✅ Workflow Management Service initialized successfully")
    
    def _initialize_workflow_templates(self) -> Dict:
        """Initialize predefined workflow templates"""
        return {
            "standard_medical_review": {
                "name": "Standard Medical Review",
                "type": WorkflowType.MEDICAL_REVIEW,
                "description": "Standard workflow for medical document review",
                "steps": [
                    {
                        "step_id": "initial_review",
                        "name": "Initial Review",
                        "type": WorkflowStep.INITIAL_REVIEW,
                        "required_role": "reviewer",
                        "estimated_duration": 24,  # hours
                        "auto_approve": False,
                        "notifications": ["assignee", "creator"]
                    },
                    {
                        "step_id": "medical_review",
                        "name": "Medical Review",
                        "type": WorkflowStep.MEDICAL_REVIEW,
                        "required_role": "medical_reviewer",
                        "estimated_duration": 48,
                        "auto_approve": False,
                        "notifications": ["assignee", "creator", "stakeholders"]
                    },
                    {
                        "step_id": "final_approval",
                        "name": "Final Approval",
                        "type": WorkflowStep.FINAL_APPROVAL,
                        "required_role": "approver",
                        "estimated_duration": 24,
                        "auto_approve": False,
                        "notifications": ["assignee", "creator", "stakeholders"]
                    }
                ],
                "escalation_rules": {
                    "overdue_threshold": 72,  # hours
                    "escalation_roles": ["supervisor", "manager"]
                }
            },
            "compliance_check": {
                "name": "Compliance Check",
                "type": WorkflowType.COMPLIANCE_CHECK,
                "description": "Workflow for compliance and regulatory checks",
                "steps": [
                    {
                        "step_id": "compliance_review",
                        "name": "Compliance Review",
                        "type": WorkflowStep.COMPLIANCE_CHECK,
                        "required_role": "compliance_officer",
                        "estimated_duration": 72,
                        "auto_approve": False,
                        "notifications": ["assignee", "creator"]
                    },
                    {
                        "step_id": "quality_assurance",
                        "name": "Quality Assurance",
                        "type": WorkflowStep.QUALITY_ASSURANCE,
                        "required_role": "qa_specialist",
                        "estimated_duration": 48,
                        "auto_approve": False,
                        "notifications": ["assignee", "creator"]
                    }
                ],
                "escalation_rules": {
                    "overdue_threshold": 120,
                    "escalation_roles": ["compliance_manager", "legal_team"]
                }
            }
        }
    
    def create_workflow(self, document_id: str, workflow_type: str, 
                       assignees: Dict[str, str], metadata: Dict = None) -> Dict:
        """
        Create a new workflow for document processing
        
        Args:
            document_id: ID of the document
            workflow_type: Type of workflow to create
            assignees: Dictionary of step_id to user_id assignments
            metadata: Additional workflow metadata
            
        Returns:
            Dict containing workflow information
        """
        try:
            # Validate workflow type
            if workflow_type not in self.workflow_templates:
                return {
                    "success": False,
                    "error": f"Unknown workflow type: {workflow_type}"
                }
            
            template = self.workflow_templates[workflow_type]
            workflow_id = str(uuid.uuid4())
            
            # Create workflow instance
            workflow = {
                "id": workflow_id,
                "document_id": document_id,
                "type": workflow_type,
                "template": template,
                "status": WorkflowStatus.DRAFT.value,
                "current_step": 0,
                "steps": [],
                "assignees": assignees,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "started_at": None,
                "completed_at": None,
                "total_duration": None,
                "history": []
            }
            
            # Initialize workflow steps
            for i, step_template in enumerate(template["steps"]):
                step = {
                    "step_id": step_template["step_id"],
                    "name": step_template["name"],
                    "type": step_template["type"].value,
                    "required_role": step_template["required_role"],
                    "assignee": assignees.get(step_template["step_id"]),
                    "status": "pending" if i == 0 else "not_started",
                    "started_at": None,
                    "completed_at": None,
                    "duration": None,
                    "comments": [],
                    "approval_status": None,
                    "auto_approve": step_template["auto_approve"]
                }
                workflow["steps"].append(step)
            
            # Store workflow
            self.workflows[workflow_id] = workflow
            
            # Add to history
            workflow["history"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "action": "workflow_created",
                "user_id": metadata.get("created_by", "system"),
                "details": f"Workflow created for document {document_id}"
            })
            
            logger.info(f"✅ Created workflow {workflow_id} for document {document_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "workflow": workflow
            }
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def start_workflow(self, workflow_id: str, user_id: str) -> Dict:
        """
        Start a workflow
        
        Args:
            workflow_id: ID of the workflow to start
            user_id: ID of the user starting the workflow
            
        Returns:
            Dict containing workflow status
        """
        try:
            if workflow_id not in self.workflows:
                return {
                    "success": False,
                    "error": "Workflow not found"
                }
            
            workflow = self.workflows[workflow_id]
            
            if workflow["status"] != WorkflowStatus.DRAFT.value:
                return {
                    "success": False,
                    "error": f"Workflow cannot be started from status: {workflow['status']}"
                }
            
            # Update workflow status
            workflow["status"] = WorkflowStatus.PENDING_REVIEW.value
            workflow["started_at"] = datetime.utcnow().isoformat()
            workflow["updated_at"] = datetime.utcnow().isoformat()
            
            # Start first step
            if workflow["steps"]:
                workflow["steps"][0]["status"] = "in_progress"
                workflow["steps"][0]["started_at"] = datetime.utcnow().isoformat()
                workflow["current_step"] = 0
            
            # Add to history
            workflow["history"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "action": "workflow_started",
                "user_id": user_id,
                "details": "Workflow started"
            })
            
            logger.info(f"✅ Started workflow {workflow_id}")
            
            return {
                "success": True,
                "workflow": workflow
            }
            
        except Exception as e:
            logger.error(f"Error starting workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_workflow_step(self, workflow_id: str, step_id: str, 
                            action: str, user_id: str, comments: str = None,
                            metadata: Dict = None) -> Dict:
        """
        Process a workflow step (approve, reject, request changes)
        
        Args:
            workflow_id: ID of the workflow
            step_id: ID of the step to process
            action: Action to take (approve, reject, request_changes)
            user_id: ID of the user taking the action
            comments: Optional comments
            metadata: Additional metadata
            
        Returns:
            Dict containing workflow status
        """
        try:
            if workflow_id not in self.workflows:
                return {
                    "success": False,
                    "error": "Workflow not found"
                }
            
            workflow = self.workflows[workflow_id]
            
            # Find the step
            step_index = None
            for i, step in enumerate(workflow["steps"]):
                if step["step_id"] == step_id:
                    step_index = i
                    break
            
            if step_index is None:
                return {
                    "success": False,
                    "error": f"Step {step_id} not found in workflow"
                }
            
            step = workflow["steps"][step_index]
            
            # Validate action
            if action not in ["approve", "reject", "request_changes"]:
                return {
                    "success": False,
                    "error": f"Invalid action: {action}"
                }
            
            # Process the action
            step["status"] = "completed"
            step["completed_at"] = datetime.utcnow().isoformat()
            step["approval_status"] = action
            
            if step["started_at"]:
                start_time = datetime.fromisoformat(step["started_at"])
                end_time = datetime.utcnow()
                step["duration"] = (end_time - start_time).total_seconds() / 3600  # hours
            
            # Add comments
            if comments:
                step["comments"].append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "comment": comments
                })
            
            # Add to history
            workflow["history"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "action": f"step_{action}",
                "user_id": user_id,
                "details": f"Step {step_id} {action}d",
                "metadata": metadata
            })
            
            # Determine next action based on current action
            if action == "reject":
                workflow["status"] = WorkflowStatus.REJECTED.value
                workflow["completed_at"] = datetime.utcnow().isoformat()
            elif action == "request_changes":
                workflow["status"] = WorkflowStatus.REQUIRES_CHANGES.value
                # Reset current step to allow resubmission
                step["status"] = "pending"
                step["started_at"] = None
                step["completed_at"] = None
                step["duration"] = None
                step["approval_status"] = None
            else:  # approve
                # Move to next step or complete workflow
                if step_index + 1 < len(workflow["steps"]):
                    # Move to next step
                    workflow["current_step"] = step_index + 1
                    next_step = workflow["steps"][step_index + 1]
                    next_step["status"] = "in_progress"
                    next_step["started_at"] = datetime.utcnow().isoformat()
                    workflow["status"] = WorkflowStatus.UNDER_REVIEW.value
                else:
                    # Complete workflow
                    workflow["status"] = WorkflowStatus.APPROVED.value
                    workflow["completed_at"] = datetime.utcnow().isoformat()
                    workflow["current_step"] = len(workflow["steps"]) - 1
            
            workflow["updated_at"] = datetime.utcnow().isoformat()
            
            # Calculate total duration if completed
            if workflow["completed_at"] and workflow["started_at"]:
                start_time = datetime.fromisoformat(workflow["started_at"])
                end_time = datetime.fromisoformat(workflow["completed_at"])
                workflow["total_duration"] = (end_time - start_time).total_seconds() / 3600
            
            logger.info(f"✅ Processed step {step_id} in workflow {workflow_id} with action: {action}")
            
            return {
                "success": True,
                "workflow": workflow,
                "next_action": "workflow_completed" if workflow["status"] == WorkflowStatus.APPROVED.value else "continue"
            }
            
        except Exception as e:
            logger.error(f"Error processing workflow step: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """
        Get workflow status and details
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Dict containing workflow status
        """
        try:
            if workflow_id not in self.workflows:
                return {
                    "success": False,
                    "error": "Workflow not found"
                }
            
            workflow = self.workflows[workflow_id]
            
            # Calculate progress
            completed_steps = sum(1 for step in workflow["steps"] if step["status"] == "completed")
            total_steps = len(workflow["steps"])
            progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0
            
            # Get current step info
            current_step = None
            if workflow["current_step"] < len(workflow["steps"]):
                current_step = workflow["steps"][workflow["current_step"]]
            
            return {
                "success": True,
                "workflow": {
                    "id": workflow["id"],
                    "document_id": workflow["document_id"],
                    "type": workflow["type"],
                    "status": workflow["status"],
                    "progress": progress,
                    "current_step": current_step,
                    "total_steps": total_steps,
                    "completed_steps": completed_steps,
                    "started_at": workflow["started_at"],
                    "completed_at": workflow["completed_at"],
                    "total_duration": workflow["total_duration"],
                    "assignees": workflow["assignees"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_workflows(self, filters: Dict = None, limit: int = 50) -> Dict:
        """
        List workflows with optional filtering
        
        Args:
            filters: Optional filters (status, type, assignee, date_range)
            limit: Maximum number of workflows to return
            
        Returns:
            Dict containing list of workflows
        """
        try:
            workflows = list(self.workflows.values())
            
            # Apply filters
            if filters:
                if filters.get("status"):
                    workflows = [w for w in workflows if w["status"] == filters["status"]]
                
                if filters.get("type"):
                    workflows = [w for w in workflows if w["type"] == filters["type"]]
                
                if filters.get("assignee"):
                    workflows = [w for w in workflows if filters["assignee"] in w["assignees"].values()]
                
                if filters.get("date_range"):
                    start_date = datetime.fromisoformat(filters["date_range"]["start"])
                    end_date = datetime.fromisoformat(filters["date_range"]["end"])
                    workflows = [w for w in workflows if 
                               start_date <= datetime.fromisoformat(w["created_at"]) <= end_date]
            
            # Sort by creation date (newest first)
            workflows.sort(key=lambda x: x["created_at"], reverse=True)
            
            # Apply limit
            workflows = workflows[:limit]
            
            return {
                "success": True,
                "workflows": workflows,
                "total": len(workflows),
                "filters_applied": filters or {}
            }
            
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_workflow_analytics(self) -> Dict:
        """Get workflow analytics and statistics"""
        try:
            total_workflows = len(self.workflows)
            
            if total_workflows == 0:
                return {
                    "success": True,
                    "analytics": {
                        "total_workflows": 0,
                        "status_distribution": {},
                        "type_distribution": {},
                        "average_duration": 0,
                        "completion_rate": 0
                    }
                }
            
            # Status distribution
            status_counts = {}
            type_counts = {}
            durations = []
            completed_count = 0
            
            for workflow in self.workflows.values():
                # Status counts
                status = workflow["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Type counts
                workflow_type = workflow["type"]
                type_counts[workflow_type] = type_counts.get(workflow_type, 0) + 1
                
                # Duration and completion
                if workflow["total_duration"]:
                    durations.append(workflow["total_duration"])
                
                if workflow["status"] in [WorkflowStatus.APPROVED.value, WorkflowStatus.REJECTED.value]:
                    completed_count += 1
            
            # Calculate averages
            average_duration = sum(durations) / len(durations) if durations else 0
            completion_rate = (completed_count / total_workflows) * 100 if total_workflows > 0 else 0
            
            return {
                "success": True,
                "analytics": {
                    "total_workflows": total_workflows,
                    "status_distribution": status_counts,
                    "type_distribution": type_counts,
                    "average_duration": round(average_duration, 2),
                    "completion_rate": round(completion_rate, 2),
                    "completed_workflows": completed_count,
                    "active_workflows": total_workflows - completed_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow analytics: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_service_status(self) -> Dict:
        """Get workflow service status"""
        return {
            "service_name": "WorkflowService",
            "status": "active",
            "total_workflows": len(self.workflows),
            "workflow_templates": list(self.workflow_templates.keys()),
            "capabilities": {
                "workflow_creation": True,
                "step_processing": True,
                "approval_workflows": True,
                "escalation_rules": True,
                "analytics": True
            }
        }
