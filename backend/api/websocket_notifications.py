"""
WebSocket Notifications Router for Phase 4
Handles real-time notification connections and message routing
"""
import os
import logging
import json
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse
import uuid
from datetime import datetime
from dataclasses import asdict

# Import notification service
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket Notifications"])

# Initialize notification service
notification_service = NotificationService()

# HTML page for testing WebSocket connections
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>DocuGenie Ultra - WebSocket Notifications Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .connected { background-color: #d4edda; color: #155724; }
        .disconnected { background-color: #f8d7da; color: #721c24; }
        .notification { background-color: #fff3cd; color: #856404; padding: 10px; margin: 5px 0; border-radius: 5px; }
        .controls { margin: 20px 0; }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
        .connect { background-color: #28a745; color: white; }
        .disconnect { background-color: #dc3545; color: white; }
        .send { background-color: #007bff; color: white; }
        input, textarea { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        .log { background-color: #f8f9fa; padding: 10px; border-radius: 5px; max-height: 300px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔔 DocuGenie Ultra - WebSocket Notifications Test</h1>
        
        <div class="controls">
            <label for="userId">User ID:</label>
            <input type="text" id="userId" value="test_user_001" placeholder="Enter user ID">
            
            <button class="connect" onclick="connectWebSocket()">Connect</button>
            <button class="disconnect" onclick="disconnectWebSocket()" disabled>Disconnect</button>
        </div>
        
        <div id="status" class="status disconnected">Disconnected</div>
        
        <div class="controls">
            <h3>Send Test Notification</h3>
            <label for="notificationType">Type:</label>
            <select id="notificationType">
                <option value="document_processed">Document Processed</option>
                <option value="workflow_updated">Workflow Updated</option>
                <option value="compliance_alert">Compliance Alert</option>
                <option value="system_alert">System Alert</option>
                <option value="user_mention">User Mention</option>
                <option value="task_assigned">Task Assigned</option>
                <option value="deadline_reminder">Deadline Reminder</option>
            </select>
            
            <label for="notificationTitle">Title:</label>
            <input type="text" id="notificationTitle" placeholder="Notification title">
            
            <label for="notificationMessage">Message:</label>
            <textarea id="notificationMessage" rows="3" placeholder="Notification message"></textarea>
            
            <label for="notificationPriority">Priority:</label>
            <select id="notificationPriority">
                <option value="low">Low</option>
                <option value="medium" selected>Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
            </select>
            
            <button class="send" onclick="sendTestNotification()">Send Test Notification</button>
        </div>
        
        <div class="controls">
            <h3>Notifications Log</h3>
            <div id="log" class="log"></div>
        </div>
    </div>

    <script>
        let ws = null;
        let userId = 'test_user_001';
        
        function updateStatus(message, isConnected) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + (isConnected ? 'connected' : 'disconnected');
            
            document.querySelector('.connect').disabled = isConnected;
            document.querySelector('.disconnect').disabled = !isConnected;
        }
        
        function addLog(message, type = 'info') {
            const log = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.innerHTML = `<strong>[${timestamp}]</strong> ${message}`;
            logEntry.className = 'notification';
            log.insertBefore(logEntry, log.firstChild);
        }
        
        function connectWebSocket() {
            userId = document.getElementById('userId').value || 'test_user_001';
            const wsUrl = `ws://${window.location.host}/ws/notifications/${userId}`;
            
            try {
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    updateStatus('Connected to WebSocket', true);
                    addLog('WebSocket connection established');
                };
                
                ws.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.type === 'notification') {
                            const notification = data.data;
                            addLog(`📢 ${notification.title}: ${notification.message}`, 'notification');
                        } else {
                            addLog(`📨 Message: ${JSON.stringify(data)}`);
                        }
                    } catch (e) {
                        addLog(`📨 Raw message: ${event.data}`);
                    }
                };
                
                ws.onclose = function(event) {
                    updateStatus('Disconnected from WebSocket', false);
                    addLog('WebSocket connection closed');
                    ws = null;
                };
                
                ws.onerror = function(error) {
                    addLog(`❌ WebSocket error: ${error}`, 'error');
                    updateStatus('Connection error', false);
                };
                
            } catch (error) {
                addLog(`❌ Failed to create WebSocket: ${error}`, 'error');
            }
        }
        
        function disconnectWebSocket() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }
        
        async function sendTestNotification() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                addLog('❌ WebSocket not connected', 'error');
                return;
            }
            
            const type = document.getElementById('notificationType').value;
            const title = document.getElementById('notificationTitle').value || 'Test Notification';
            const message = document.getElementById('notificationMessage').value || 'This is a test notification';
            const priority = document.getElementById('notificationPriority').value;
            
            try {
                const response = await fetch('/api/v1/notifications/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id: userId,
                        notification_type: type,
                        title: title,
                        message: message,
                        priority: priority
                    })
                });
                
                if (response.ok) {
                    addLog(`✅ Test notification sent: ${title}`, 'success');
                } else {
                    const error = await response.text();
                    addLog(`❌ Failed to send notification: ${error}`, 'error');
                }
            } catch (error) {
                addLog(`❌ Error sending notification: ${error}`, 'error');
            }
        }
        
        // Auto-connect on page load
        window.onload = function() {
            setTimeout(connectWebSocket, 1000);
        };
    </script>
</body>
</html>
"""

@router.get("/test", response_class=HTMLResponse)
async def get_websocket_test_page():
    """Get HTML test page for WebSocket notifications"""
    return HTMLResponse(content=html_page)

@router.websocket("/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications"""
    try:
        # Connect to notification service
        success = await notification_service.connect_websocket(websocket, user_id)
        
        if not success:
            await websocket.close(code=1000, reason="Failed to initialize notification service")
            return
        
        # Keep connection alive and handle messages
        try:
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    logger.info(f"📨 Received message from user {user_id}: {message}")
                    
                    # Handle different message types
                    if message.get("type") == "ping":
                        # Respond to ping with pong
                        await websocket.send_text(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                    
                    elif message.get("type") == "get_notifications":
                        # Send user's notifications
                        notifications = notification_service.get_user_notifications(
                            user_id,
                            limit=message.get("limit", 50),
                            unread_only=message.get("unread_only", False)
                        )
                        
                        await websocket.send_text(json.dumps({
                            "type": "notifications_list",
                            "data": [asdict(n) for n in notifications],
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                    
                    elif message.get("type") == "mark_read":
                        # Mark notification as read
                        notification_id = message.get("notification_id")
                        if notification_id:
                            success = await notification_service.mark_notification_read(user_id, notification_id)
                            await websocket.send_text(json.dumps({
                                "type": "mark_read_response",
                                "success": success,
                                "notification_id": notification_id,
                                "timestamp": datetime.utcnow().isoformat()
                            }))
                    
                    else:
                        # Unknown message type
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": f"Unknown message type: {message.get('type')}",
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON message",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                
        except WebSocketDisconnect:
            logger.info(f"🔌 WebSocket disconnected for user: {user_id}")
        except Exception as e:
            logger.error(f"❌ WebSocket error for user {user_id}: {e}")
            await websocket.close(code=1011, reason=f"Internal error: {str(e)}")
        
        finally:
            # Clean up connection
            await notification_service.disconnect_websocket(user_id)
    
    except Exception as e:
        logger.error(f"❌ WebSocket connection failed for user {user_id}: {e}")
        try:
            await websocket.close(code=1011, reason=f"Connection failed: {str(e)}")
        except:
            pass

@router.get("/status")
async def get_websocket_status():
    """Get WebSocket service status"""
    try:
        status = notification_service.get_service_status()
        return {
            "success": True,
            "websocket_service": status,
            "active_connections": len(notification_service.active_connections),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting WebSocket status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connections")
async def get_active_connections():
    """Get list of active WebSocket connections"""
    try:
        connections = list(notification_service.active_connections.keys())
        return {
            "success": True,
            "active_connections": connections,
            "total_connections": len(connections),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting active connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast")
async def broadcast_message(message: str, priority: str = "medium"):
    """Broadcast a message to all connected users"""
    try:
        success = await notification_service.send_system_notification(message, priority)
        return {
            "success": success,
            "message": "System message broadcast",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
