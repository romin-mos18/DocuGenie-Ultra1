"""
Notifications API Router for Phase 4
HTTP endpoints for notification management and operations
"""
import os
import logging
import json
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel
from datetime import datetime
import uuid

# Import notification service
from services.notification_service import NotificationService, NotificationType, NotificationPriority, NotificationStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Initialize notification service
notification_service = NotificationService()

# Pydantic models for request/response
class SendNotificationRequest(BaseModel):
    user_id: str
    notification_type: str
    title: str
    message: str
    priority: str = NotificationPriority.MEDIUM.value
    metadata: Optional[Dict[str, Any]] = None

class BulkNotificationRequest(BaseModel):
    user_ids: List[str]
    notification_type: str
    title: str
    message: str
    priority: str = NotificationPriority.MEDIUM.value
    metadata: Optional[Dict[str, Any]] = None

class SystemNotificationRequest(BaseModel):
    message: str
    priority: str = NotificationPriority.MEDIUM.value
    metadata: Optional[Dict[str, Any]] = None

class MarkReadRequest(BaseModel):
    notification_id: str

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    priority: str
    status: str
    created_at: datetime
    read_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

# Notification Management Endpoints
@router.post("/send")
async def send_notification(request: SendNotificationRequest):
    """Send a notification to a specific user"""
    try:
        success = await notification_service.send_notification_to_user(
            user_id=request.user_id,
            notification_type=request.notification_type,
            title=request.title,
            message=request.message,
            priority=request.priority,
            metadata=request.metadata
        )
        
        if success:
            return {
                "success": True,
                "message": "Notification sent successfully",
                "user_id": request.user_id,
                "notification_type": request.notification_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send notification")
            
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send/bulk")
async def send_bulk_notifications(request: BulkNotificationRequest):
    """Send notifications to multiple users"""
    try:
        results = await notification_service.send_bulk_notifications(
            user_ids=request.user_ids,
            notification_type=request.notification_type,
            title=request.title,
            message=request.message,
            priority=request.priority,
            metadata=request.metadata
        )
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(request.user_ids)
        
        return {
            "success": True,
            "message": f"Bulk notifications sent: {success_count}/{total_count} successful",
            "results": results,
            "success_count": success_count,
            "total_count": total_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error sending bulk notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send/system")
async def send_system_notification(request: SystemNotificationRequest):
    """Send a system-wide notification to all connected users"""
    try:
        success = await notification_service.send_system_notification(
            message=request.message,
            priority=request.priority,
            metadata=request.metadata
        )
        
        return {
            "success": success,
            "message": "System notification sent",
            "priority": request.priority,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error sending system notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Notification Retrieval Endpoints
@router.get("/user/{user_id}")
async def get_user_notifications(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    notification_type: Optional[str] = Query(None)
):
    """Get notifications for a specific user"""
    try:
        notifications = notification_service.get_user_notifications(
            user_id=user_id,
            limit=limit,
            unread_only=unread_only,
            notification_type=notification_type
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "notifications": [asdict(n) for n in notifications],
            "total_count": len(notifications),
            "filters": {
                "limit": limit,
                "unread_only": unread_only,
                "notification_type": notification_type
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting notifications for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/stats")
async def get_user_notification_stats(user_id: str):
    """Get notification statistics for a specific user"""
    try:
        stats = notification_service.get_notification_stats(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting notification stats for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/unread")
async def get_unread_notifications(user_id: str, limit: int = Query(50, ge=1, le=100)):
    """Get unread notifications for a specific user"""
    try:
        notifications = notification_service.get_user_notifications(
            user_id=user_id,
            limit=limit,
            unread_only=True
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "unread_notifications": [asdict(n) for n in notifications],
            "unread_count": len(notifications),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting unread notifications for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Notification Status Management
@router.post("/user/{user_id}/mark-read")
async def mark_notification_read(user_id: str, request: MarkReadRequest):
    """Mark a specific notification as read"""
    try:
        success = await notification_service.mark_notification_read(
            user_id=user_id,
            notification_id=request.notification_id
        )
        
        if success:
            return {
                "success": True,
                "message": "Notification marked as read",
                "user_id": user_id,
                "notification_id": request.notification_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
            
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user/{user_id}/mark-all-read")
async def mark_all_notifications_read(user_id: str):
    """Mark all notifications as read for a specific user"""
    try:
        count = await notification_service.mark_all_notifications_read(user_id)
        
        return {
            "success": True,
            "message": f"Marked {count} notifications as read",
            "user_id": user_id,
            "marked_count": count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Service Management Endpoints
@router.get("/status")
async def get_notification_service_status():
    """Get notification service status and capabilities"""
    try:
        status = notification_service.get_service_status()
        
        return {
            "success": True,
            "notification_service": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting notification service status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_notification_templates():
    """Get available notification templates"""
    try:
        templates = notification_service.notification_templates
        
        return {
            "success": True,
            "templates": templates,
            "total_templates": len(templates),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting notification templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types")
async def get_notification_types():
    """Get available notification types"""
    try:
        types = [nt.value for nt in NotificationType]
        priorities = [np.value for np in NotificationPriority]
        statuses = [ns.value for ns in NotificationStatus]
        
        return {
            "success": True,
            "notification_types": types,
            "priority_levels": priorities,
            "status_types": statuses,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting notification types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility Endpoints
@router.post("/cleanup")
async def cleanup_expired_notifications():
    """Clean up expired notifications"""
    try:
        count = notification_service.cleanup_expired_notifications()
        
        return {
            "success": True,
            "message": f"Cleaned up expired notifications for {count} users",
            "cleanup_count": count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up expired notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def notification_health_check():
    """Health check for notification service"""
    try:
        status = notification_service.get_service_status()
        
        # Check if service is operational
        is_healthy = (
            status.get("status") == "active" and
            status.get("websocket_available") is not None
        )
        
        return {
            "success": True,
            "healthy": is_healthy,
            "status": "healthy" if is_healthy else "unhealthy",
            "service": status.get("service_name"),
            "capabilities": status.get("capabilities", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Notification health check failed: {e}")
        return {
            "success": False,
            "healthy": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
