"""
Notification Service for Phase 4: Real-time Notifications
Provides real-time alerts, event handling, and user notification management
"""
import os
import logging
import json
import asyncio
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import uuid
from dataclasses import dataclass, asdict

# WebSocket imports
try:
    from fastapi import WebSocket, WebSocketDisconnect
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("⚠️ WebSocket support not available. Please install: pip install fastapi")

# Redis imports for caching and pub/sub
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available. Please install: pip install redis")

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Notification type enumeration"""
    DOCUMENT_PROCESSED = "document_processed"
    WORKFLOW_UPDATED = "workflow_updated"
    COMPLIANCE_ALERT = "compliance_alert"
    SYSTEM_ALERT = "system_alert"
    USER_MENTION = "user_mention"
    TASK_ASSIGNED = "task_assigned"
    DEADLINE_REMINDER = "deadline_reminder"
    SUCCESS_MESSAGE = "success_message"
    ERROR_MESSAGE = "error_message"
    INFO_MESSAGE = "info_message"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

@dataclass
class Notification:
    """Notification data structure"""
    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    status: NotificationStatus
    created_at: datetime
    read_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

class NotificationService:
    """Real-time notification service with WebSocket support"""
    
    def __init__(self):
        """Initialize notification service"""
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_notifications: Dict[str, List[Notification]] = {}
        self.notification_templates = self._initialize_notification_templates()
        self.redis_client = None
        self.redis_pubsub = None
        
        # Initialize Redis if available
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    db=0,
                    decode_responses=True
                )
                self.redis_pubsub = self.redis_client.pubsub()
                logger.info("✅ Redis client initialized for notifications")
            except Exception as e:
                logger.warning(f"Could not initialize Redis: {e}")
                self.redis_client = None
        
        logger.info("✅ Notification Service initialized successfully")
    
    def _initialize_notification_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize notification templates for different types"""
        return {
            NotificationType.DOCUMENT_PROCESSED.value: {
                "title": "Document Processing Complete",
                "message": "Your document '{filename}' has been processed successfully.",
                "priority": NotificationPriority.MEDIUM.value,
                "icon": "📄",
                "color": "green"
            },
            NotificationType.WORKFLOW_UPDATED.value: {
                "title": "Workflow Update",
                "message": "Workflow '{workflow_name}' has been updated. Status: {status}",
                "priority": NotificationPriority.HIGH.value,
                "icon": "🔄",
                "color": "blue"
            },
            NotificationType.COMPLIANCE_ALERT.value: {
                "title": "Compliance Alert",
                "message": "Compliance issue detected in document '{filename}'. Risk level: {risk_level}",
                "priority": NotificationPriority.CRITICAL.value,
                "icon": "⚠️",
                "color": "red"
            },
            NotificationType.SYSTEM_ALERT.value: {
                "title": "System Alert",
                "message": "System notification: {message}",
                "priority": NotificationPriority.HIGH.value,
                "icon": "🔔",
                "color": "orange"
            },
            NotificationType.USER_MENTION.value: {
                "title": "You were mentioned",
                "message": "{user_name} mentioned you in {context}",
                "priority": NotificationPriority.MEDIUM.value,
                "icon": "👤",
                "color": "blue"
            },
            NotificationType.TASK_ASSIGNED.value: {
                "title": "Task Assigned",
                "message": "You have been assigned a new task: {task_name}",
                "priority": NotificationPriority.HIGH.value,
                "icon": "📋",
                "color": "purple"
            },
            NotificationType.DEADLINE_REMINDER.value: {
                "title": "Deadline Reminder",
                "message": "Reminder: {task_name} is due in {time_remaining}",
                "priority": NotificationPriority.HIGH.value,
                "icon": "⏰",
                "color": "orange"
            }
        }
    
    async def connect_websocket(self, websocket: WebSocket, user_id: str):
        """Connect a user's WebSocket for real-time notifications"""
        try:
            await websocket.accept()
            self.active_connections[user_id] = websocket
            
            # Send connection confirmation
            await self.send_notification_to_user(
                user_id,
                NotificationType.SUCCESS_MESSAGE.value,
                "Connected to real-time notifications",
                "Connection established successfully",
                NotificationPriority.LOW.value,
                {"connection_id": str(uuid.uuid4())}
            )
            
            logger.info(f"✅ WebSocket connected for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed for user {user_id}: {e}")
            return False
    
    async def disconnect_websocket(self, user_id: str):
        """Disconnect a user's WebSocket"""
        try:
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                await websocket.close()
                del self.active_connections[user_id]
                logger.info(f"✅ WebSocket disconnected for user: {user_id}")
                return True
        except Exception as e:
            logger.error(f"❌ WebSocket disconnection failed for user {user_id}: {e}")
        
        return False
    
    async def send_notification_to_user(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        priority: str = NotificationPriority.MEDIUM.value,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a notification to a specific user"""
        try:
            # Create notification object
            notification = Notification(
                id=str(uuid.uuid4()),
                user_id=user_id,
                type=NotificationType(notification_type),
                title=title,
                message=message,
                priority=NotificationPriority(priority),
                status=NotificationStatus.PENDING,
                created_at=datetime.utcnow(),
                metadata=metadata or {},
                expires_at=datetime.utcnow() + timedelta(days=30)  # 30 day expiry
            )
            
            # Store notification
            if user_id not in self.user_notifications:
                self.user_notifications[user_id] = []
            self.user_notifications[user_id].append(notification)
            
            # Send via WebSocket if connected
            if user_id in self.active_connections:
                await self._send_websocket_notification(user_id, notification)
                notification.status = NotificationStatus.SENT
            
            # Publish to Redis if available
            if self.redis_client:
                await self._publish_notification_to_redis(notification)
            
            logger.info(f"✅ Notification sent to user {user_id}: {title}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send notification to user {user_id}: {e}")
            return False
    
    async def send_bulk_notifications(
        self,
        user_ids: List[str],
        notification_type: str,
        title: str,
        message: str,
        priority: str = NotificationPriority.MEDIUM.value,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Send notifications to multiple users"""
        results = {}
        
        for user_id in user_ids:
            success = await self.send_notification_to_user(
                user_id, notification_type, title, message, priority, metadata
            )
            results[user_id] = success
        
        return results
    
    async def send_system_notification(
        self,
        message: str,
        priority: str = NotificationPriority.MEDIUM.value,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a system-wide notification"""
        try:
            # Get all connected users
            user_ids = list(self.active_connections.keys())
            
            if user_ids:
                results = await self.send_bulk_notifications(
                    user_ids,
                    NotificationType.SYSTEM_ALERT.value,
                    "System Notification",
                    message,
                    priority,
                    metadata
                )
                
                success_count = sum(1 for success in results.values() if success)
                logger.info(f"✅ System notification sent to {success_count}/{len(user_ids)} users")
                return success_count > 0
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to send system notification: {e}")
            return False
    
    async def _send_websocket_notification(self, user_id: str, notification: Notification):
        """Send notification via WebSocket"""
        try:
            websocket = self.active_connections[user_id]
            
            # Prepare notification data
            notification_data = {
                "type": "notification",
                "data": asdict(notification),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(notification_data, default=str))
            logger.debug(f"✅ WebSocket notification sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ WebSocket notification failed for user {user_id}: {e}")
            # Remove failed connection
            if user_id in self.active_connections:
                del self.active_connections[user_id]
    
    async def _publish_notification_to_redis(self, notification: Notification):
        """Publish notification to Redis for other services"""
        try:
            if self.redis_client:
                channel = f"notifications:{notification.user_id}"
                message = json.dumps(asdict(notification), default=str)
                self.redis_client.publish(channel, message)
                logger.debug(f"✅ Notification published to Redis channel: {channel}")
        except Exception as e:
            logger.warning(f"Could not publish to Redis: {e}")
    
    async def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        """Mark a notification as read"""
        try:
            if user_id in self.user_notifications:
                for notification in self.user_notifications[user_id]:
                    if notification.id == notification_id:
                        notification.status = NotificationStatus.READ
                        notification.read_at = datetime.utcnow()
                        logger.info(f"✅ Notification {notification_id} marked as read")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to mark notification as read: {e}")
            return False
    
    async def mark_all_notifications_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        try:
            count = 0
            if user_id in self.user_notifications:
                for notification in self.user_notifications[user_id]:
                    if notification.status != NotificationStatus.READ:
                        notification.status = NotificationStatus.READ
                        notification.read_at = datetime.utcnow()
                        count += 1
            
            logger.info(f"✅ Marked {count} notifications as read for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"❌ Failed to mark all notifications as read: {e}")
            return 0
    
    def get_user_notifications(
        self,
        user_id: str,
        limit: int = 50,
        unread_only: bool = False,
        notification_type: Optional[str] = None
    ) -> List[Notification]:
        """Get notifications for a specific user"""
        try:
            if user_id not in self.user_notifications:
                return []
            
            notifications = self.user_notifications[user_id]
            
            # Apply filters
            if unread_only:
                notifications = [n for n in notifications if n.status != NotificationStatus.READ]
            
            if notification_type:
                notifications = [n for n in notifications if n.type.value == notification_type]
            
            # Sort by creation date (newest first) and limit
            notifications.sort(key=lambda x: x.created_at, reverse=True)
            return notifications[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to get notifications for user {user_id}: {e}")
            return []
    
    def get_notification_stats(self, user_id: str) -> Dict[str, Any]:
        """Get notification statistics for a user"""
        try:
            if user_id not in self.user_notifications:
                return {
                    "total": 0,
                    "unread": 0,
                    "by_type": {},
                    "by_priority": {}
                }
            
            notifications = self.user_notifications[user_id]
            
            # Count by type
            by_type = {}
            by_priority = {}
            unread_count = 0
            
            for notification in notifications:
                # Count by type
                type_key = notification.type.value
                by_type[type_key] = by_type.get(type_key, 0) + 1
                
                # Count by priority
                priority_key = notification.priority.value
                by_priority[priority_key] = by_priority.get(priority_key, 0) + 1
                
                # Count unread
                if notification.status != NotificationStatus.READ:
                    unread_count += 1
            
            return {
                "total": len(notifications),
                "unread": unread_count,
                "by_type": by_type,
                "by_priority": by_priority
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get notification stats for user {user_id}: {e}")
            return {}
    
    def cleanup_expired_notifications(self) -> int:
        """Clean up expired notifications"""
        try:
            count = 0
            current_time = datetime.utcnow()
            
            for user_id in list(self.user_notifications.keys()):
                notifications = self.user_notifications[user_id]
                # Remove expired notifications
                notifications = [n for n in notifications if not n.expires_at or n.expires_at > current_time]
                self.user_notifications[user_id] = notifications
                count += 1
            
            logger.info(f"✅ Cleaned up expired notifications for {count} users")
            return count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup expired notifications: {e}")
            return 0
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get notification service status"""
        return {
            "service_name": "NotificationService",
            "status": "active",
            "websocket_available": WEBSOCKET_AVAILABLE,
            "redis_available": REDIS_AVAILABLE is not None,
            "active_connections": len(self.active_connections),
            "total_users_with_notifications": len(self.user_notifications),
            "capabilities": {
                "real_time_notifications": WEBSOCKET_AVAILABLE,
                "bulk_notifications": True,
                "notification_templates": len(self.notification_templates),
                "user_preferences": True,
                "expiration_cleanup": True
            },
            "notification_types": [nt.value for nt in NotificationType],
            "priority_levels": [np.value for np in NotificationPriority]
        }
    
    def _create_test_notification(self, user_id: str, notification_type: str, title: str, message: str, priority: str) -> Optional[Notification]:
        """Create a test notification for testing purposes"""
        try:
            notification = Notification(
                id=str(uuid.uuid4()),
                user_id=user_id,
                type=NotificationType(notification_type),
                title=title,
                message=message,
                priority=NotificationPriority(priority),
                status=NotificationStatus.PENDING,
                created_at=datetime.utcnow(),
                metadata={"test": True},
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            
            # Store notification
            if user_id not in self.user_notifications:
                self.user_notifications[user_id] = []
            self.user_notifications[user_id].append(notification)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating test notification: {e}")
            return None
