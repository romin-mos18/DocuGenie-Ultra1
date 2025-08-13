#!/usr/bin/env python
"""
Real-time Document Intelligence Service for DocuGenie Ultra
Provides live document processing, streaming analysis, and real-time insights
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime
import json
import asyncio
import threading
import time
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import queue
from concurrent.futures import ThreadPoolExecutor

# Import other services
from services.docling_service import DoclingService
from services.rag_service import RAGService
from services.llm_service import LLMService
from services.healthcare_model_service import HealthcareModelService
from services.multilang_service import MultiLanguageService

logger = logging.getLogger(__name__)

class IntelligenceEventType(Enum):
    """Types of intelligence events"""
    DOCUMENT_UPLOADED = "document_uploaded"
    PROCESSING_STARTED = "processing_started"
    EXTRACTION_COMPLETED = "extraction_completed"
    ANALYSIS_COMPLETED = "analysis_completed"
    INSIGHT_DISCOVERED = "insight_discovered"
    COMPLIANCE_ALERT = "compliance_alert"
    CRITICAL_FINDING = "critical_finding"
    PROCESSING_ERROR = "processing_error"

@dataclass
class IntelligenceEvent:
    """Real-time intelligence event"""
    event_id: str
    event_type: IntelligenceEventType
    timestamp: datetime
    document_id: str
    filename: str
    data: Dict[str, Any]
    priority: str = "normal"
    requires_attention: bool = False

class RealTimeIntelligenceService:
    """Service for real-time document intelligence"""
    
    def __init__(self):
        """Initialize real-time intelligence service"""
        self.events_queue = queue.Queue()
        self.subscribers = {}
        self.processing_streams = {}
        self.alert_rules = self._load_alert_rules()
        self.intelligence_cache = {}
        
        # Initialize other services
        self.docling_service = DoclingService()
        self.rag_service = RAGService()
        self.llm_service = LLMService()
        self.model_service = HealthcareModelService()
        self.multilang_service = MultiLanguageService()
        
        # Start background processors
        self._start_event_processor()
        self._start_stream_processor()
        
        logger.info("✅ Real-time Intelligence Service initialized successfully")
    
    def _load_alert_rules(self) -> Dict[str, Any]:
        """Load alert rules for real-time monitoring"""
        return {
            "critical_keywords": [
                "critical", "urgent", "emergency", "severe", "dangerous",
                "immediate", "stat", "asap", "life-threatening"
            ],
            "compliance_keywords": [
                "hipaa", "violation", "breach", "unauthorized", "confidential",
                "privacy", "consent", "compliance", "regulatory"
            ],
            "medical_alerts": [
                "abnormal", "critical value", "panic value", "high risk",
                "contraindication", "allergy", "drug interaction"
            ],
            "thresholds": {
                "processing_time": 30,  # seconds
                "confidence_threshold": 0.7,
                "error_rate_threshold": 0.1
            }
        }
    
    def _start_event_processor(self):
        """Start background event processor"""
        def event_processor():
            while True:
                try:
                    event = self.events_queue.get(timeout=1)
                    if event is None:
                        break
                    
                    # Process event
                    self._process_intelligence_event(event)
                    
                    # Notify subscribers
                    self._notify_subscribers(event)
                    
                    self.events_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"❌ Event processor error: {e}")
        
        event_thread = threading.Thread(target=event_processor, daemon=True)
        event_thread.start()
        logger.info("✅ Event processor started")
    
    def _start_stream_processor(self):
        """Start background stream processor"""
        def stream_processor():
            while True:
                try:
                    # Process active streams
                    for stream_id, stream in self.processing_streams.items():
                        if stream.get("active", False):
                            self._process_stream(stream_id, stream)
                    
                    time.sleep(1)  # Check every second
                    
                except Exception as e:
                    logger.error(f"❌ Stream processor error: {e}")
        
        stream_thread = threading.Thread(target=stream_processor, daemon=True)
        stream_thread.start()
        logger.info("✅ Stream processor started")
    
    def start_document_stream(
        self, 
        stream_id: str, 
        source_directory: str,
        file_patterns: List[str] = None,
        analysis_pipeline: List[str] = None
    ) -> Dict[str, Any]:
        """Start real-time document processing stream"""
        try:
            if stream_id in self.processing_streams:
                return {
                    "success": False,
                    "error": f"Stream {stream_id} already exists"
                }
            
            # Set default file patterns
            if file_patterns is None:
                file_patterns = ["*.pdf", "*.docx", "*.txt", "*.xlsx"]
            
            # Set default analysis pipeline
            if analysis_pipeline is None:
                analysis_pipeline = ["extraction", "analysis", "intelligence"]
            
            # Create stream configuration
            stream = {
                "stream_id": stream_id,
                "source_directory": source_directory,
                "file_patterns": file_patterns,
                "analysis_pipeline": analysis_pipeline,
                "active": True,
                "started_at": datetime.now(),
                "processed_files": 0,
                "total_insights": 0,
                "alerts_generated": 0,
                "last_activity": datetime.now()
            }
            
            # Store stream
            self.processing_streams[stream_id] = stream
            
            # Emit event
            self._emit_event(
                IntelligenceEventType.PROCESSING_STARTED,
                stream_id,
                "stream_started",
                {"stream_config": stream}
            )
            
            logger.info(f"🚀 Started document stream: {stream_id}")
            
            return {
                "success": True,
                "stream_id": stream_id,
                "status": "active",
                "source_directory": source_directory,
                "analysis_pipeline": analysis_pipeline
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start document stream: {e}")
            return {
                "success": False,
                "error": f"Stream start failed: {str(e)}"
            }
    
    def stop_document_stream(self, stream_id: str) -> Dict[str, Any]:
        """Stop a document processing stream"""
        try:
            if stream_id not in self.processing_streams:
                return {
                    "success": False,
                    "error": f"Stream {stream_id} not found"
                }
            
            stream = self.processing_streams[stream_id]
            stream["active"] = False
            stream["stopped_at"] = datetime.now()
            
            # Emit event
            self._emit_event(
                IntelligenceEventType.PROCESSING_STARTED,
                stream_id,
                "stream_stopped",
                {"stream_stats": stream}
            )
            
            logger.info(f"⏹️ Stopped document stream: {stream_id}")
            
            return {
                "success": True,
                "stream_id": stream_id,
                "status": "stopped",
                "final_stats": stream
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to stop document stream: {e}")
            return {
                "success": False,
                "error": f"Stream stop failed: {str(e)}"
            }
    
    def _process_stream(self, stream_id: str, stream: Dict[str, Any]):
        """Process an active document stream"""
        try:
            # Check for new files
            new_files = self._get_new_files(stream)
            
            if new_files:
                # Process new files
                for file_path in new_files:
                    self._process_file_realtime(file_path, stream)
                    
                    # Update stream stats
                    stream["processed_files"] += 1
                    stream["last_activity"] = datetime.now()
                    
        except Exception as e:
            logger.error(f"❌ Stream processing failed: {e}")
    
    def _get_new_files(self, stream: Dict[str, Any]) -> List[str]:
        """Get new files in the stream directory"""
        try:
            new_files = []
            source_dir = Path(stream["source_directory"])
            
            for pattern in stream["file_patterns"]:
                for file_path in source_dir.glob(pattern):
                    if file_path.is_file():
                        # Check if file is new (modified in last 5 seconds)
                        if (datetime.now().timestamp() - file_path.stat().st_mtime) < 5:
                            new_files.append(str(file_path))
            
            return new_files
            
        except Exception as e:
            logger.error(f"❌ Failed to get new files: {e}")
            return []
    
    def _process_file_realtime(self, file_path: str, stream: Dict[str, Any]):
        """Process a file in real-time"""
        try:
            filename = os.path.basename(file_path)
            file_id = f"realtime_{int(time.time())}_{filename}"
            
            # Emit processing started event
            self._emit_event(
                IntelligenceEventType.PROCESSING_STARTED,
                file_id,
                filename,
                {"file_path": file_path, "stream_id": stream["stream_id"]}
            )
            
            # Process file with pipeline
            results = self._execute_realtime_pipeline(file_path, stream["analysis_pipeline"])
            
            # Generate insights
            insights = self._generate_realtime_insights(results, file_path)
            
            # Check for alerts
            alerts = self._check_alert_conditions(results, insights)
            
            # Emit completion event
            self._emit_event(
                IntelligenceEventType.ANALYSIS_COMPLETED,
                file_id,
                filename,
                {
                    "results": results,
                    "insights": insights,
                    "alerts": alerts,
                    "processing_time": results.get("processing_time", 0)
                }
            )
            
            # Update stream stats
            stream["total_insights"] += len(insights)
            stream["alerts_generated"] += len(alerts)
            
        except Exception as e:
            logger.error(f"❌ Real-time file processing failed: {e}")
            self._emit_event(
                IntelligenceEventType.PROCESSING_ERROR,
                file_id,
                filename,
                {"error": str(e)}
            )
    
    def _execute_realtime_pipeline(
        self, 
        file_path: str, 
        pipeline: List[str]
    ) -> Dict[str, Any]:
        """Execute real-time analysis pipeline"""
        try:
            results = {}
            start_time = time.time()
            
            # Basic extraction
            if "extraction" in pipeline:
                file_type = os.path.splitext(file_path)[1][1:].lower()
                extraction_result = self.docling_service.process_document(file_path, file_type)
                results["extraction"] = extraction_result
            
            # RAG processing
            if "rag" in pipeline and results.get("extraction", {}).get("success", False):
                rag_result = self.rag_service.process_document_for_rag(file_path, file_type)
                results["rag"] = rag_result
            
            # LLM analysis
            if "llm_analysis" in pipeline and results.get("extraction", {}).get("success", False):
                content = results["extraction"].get("text", "")
                if content:
                    # For now, use placeholder
                    # In production, you would call the LLM service
                    results["llm_analysis"] = {
                        "success": True,
                        "analysis_type": "realtime_summary",
                        "note": "LLM analysis requires async processing"
                    }
            
            # Model prediction
            if "model_prediction" in pipeline and results.get("extraction", {}).get("success", False):
                content = results["extraction"].get("text", "")
                if content:
                    # For now, use placeholder
                    # In production, you would use trained models
                    results["model_prediction"] = {
                        "success": True,
                        "prediction_type": "realtime_classification",
                        "note": "Model prediction requires trained models"
                    }
            
            results["processing_time"] = time.time() - start_time
            return results
            
        except Exception as e:
            logger.error(f"❌ Pipeline execution failed: {e}")
            return {"error": str(e)}
    
    def _generate_realtime_insights(
        self, 
        results: Dict[str, Any], 
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Generate real-time insights from processing results"""
        try:
            insights = []
            
            # Extraction insights
            if "extraction" in results:
                extraction = results["extraction"]
                if extraction.get("success", False):
                    insights.append({
                        "type": "extraction_success",
                        "message": f"Successfully extracted {extraction.get('word_count', 0)} words",
                        "confidence": extraction.get("confidence", 0),
                        "priority": "normal"
                    })
                    
                    # Check for critical content
                    text = extraction.get("text", "").lower()
                    if any(keyword in text for keyword in self.alert_rules["critical_keywords"]):
                        insights.append({
                            "type": "critical_content_detected",
                            "message": "Critical medical content detected",
                            "priority": "high",
                            "requires_attention": True
                        })
            
            # RAG insights
            if "rag" in results:
                rag = results["rag"]
                if rag.get("success", False):
                    insights.append({
                        "type": "rag_processing_complete",
                        "message": f"Created {rag.get('chunks_created', 0)} text chunks",
                        "priority": "normal"
                    })
            
            # Processing time insights
            processing_time = results.get("processing_time", 0)
            if processing_time > self.alert_rules["thresholds"]["processing_time"]:
                insights.append({
                    "type": "slow_processing_alert",
                    "message": f"Processing took {processing_time:.2f} seconds",
                    "priority": "medium",
                    "requires_attention": True
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Insight generation failed: {e}")
            return []
    
    def _check_alert_conditions(
        self, 
        results: Dict[str, Any], 
        insights: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        try:
            alerts = []
            
            # Check insights for high-priority items
            for insight in insights:
                if insight.get("requires_attention", False):
                    alerts.append({
                        "type": "insight_alert",
                        "message": insight["message"],
                        "priority": insight["priority"],
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Check for compliance issues
            if "extraction" in results:
                text = results["extraction"].get("text", "").lower()
                compliance_keywords = self.alert_rules["compliance_keywords"]
                found_keywords = [kw for kw in compliance_keywords if kw in text]
                
                if found_keywords:
                    alerts.append({
                        "type": "compliance_alert",
                        "message": f"Compliance keywords detected: {', '.join(found_keywords)}",
                        "priority": "high",
                        "requires_attention": True,
                        "keywords": found_keywords
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Alert checking failed: {e}")
            return []
    
    def _emit_event(
        self, 
        event_type: IntelligenceEventType, 
        document_id: str, 
        filename: str, 
        data: Dict[str, Any]
    ):
        """Emit a real-time intelligence event"""
        try:
            event = IntelligenceEvent(
                event_id=f"event_{int(time.time())}_{document_id}",
                event_type=event_type,
                timestamp=datetime.now(),
                document_id=document_id,
                filename=filename,
                data=data,
                priority="normal",
                requires_attention=False
            )
            
            # Add to queue
            self.events_queue.put(event)
            
            # Cache event
            self.intelligence_cache[event.event_id] = event
            
            # Clean old events (keep last 1000)
            if len(self.intelligence_cache) > 1000:
                oldest_events = sorted(
                    self.intelligence_cache.keys(), 
                    key=lambda k: self.intelligence_cache[k].timestamp
                )[:100]
                for old_event_id in oldest_events:
                    del self.intelligence_cache[old_event_id]
            
        except Exception as e:
            logger.error(f"❌ Failed to emit event: {e}")
    
    def _process_intelligence_event(self, event: IntelligenceEvent):
        """Process an intelligence event"""
        try:
            # Apply business logic based on event type
            if event.event_type == IntelligenceEventType.CRITICAL_FINDING:
                event.priority = "high"
                event.requires_attention = True
            
            elif event.event_type == IntelligenceEventType.COMPLIANCE_ALERT:
                event.priority = "high"
                event.requires_attention = True
            
            # Store processed event
            event.data["processed"] = True
            event.data["processed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"❌ Event processing failed: {e}")
    
    def _notify_subscribers(self, event: IntelligenceEvent):
        """Notify event subscribers"""
        try:
            for subscriber_id, callback in self.subscribers.items():
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"❌ Subscriber notification failed: {e}")
        except Exception as e:
            logger.error(f"❌ Subscriber notification failed: {e}")
    
    def subscribe_to_events(
        self, 
        subscriber_id: str, 
        callback: Callable[[IntelligenceEvent], None]
    ) -> Dict[str, Any]:
        """Subscribe to real-time intelligence events"""
        try:
            self.subscribers[subscriber_id] = callback
            
            return {
                "success": True,
                "subscriber_id": subscriber_id,
                "message": "Successfully subscribed to intelligence events"
            }
            
        except Exception as e:
            logger.error(f"❌ Event subscription failed: {e}")
            return {
                "success": False,
                "error": f"Subscription failed: {str(e)}"
            }
    
    def unsubscribe_from_events(self, subscriber_id: str) -> Dict[str, Any]:
        """Unsubscribe from real-time intelligence events"""
        try:
            if subscriber_id in self.subscribers:
                del self.subscribers[subscriber_id]
                
                return {
                    "success": True,
                    "subscriber_id": subscriber_id,
                    "message": "Successfully unsubscribed from intelligence events"
                }
            else:
                return {
                    "success": False,
                    "error": f"Subscriber {subscriber_id} not found"
                }
                
        except Exception as e:
            logger.error(f"❌ Event unsubscription failed: {e}")
            return {
                "success": False,
                "error": f"Unsubscription failed: {str(e)}"
            }
    
    def get_stream_status(self, stream_id: str = None) -> Dict[str, Any]:
        """Get status of document streams"""
        try:
            if stream_id:
                if stream_id not in self.processing_streams:
                    return {
                        "success": False,
                        "error": f"Stream {stream_id} not found"
                    }
                
                return {
                    "success": True,
                    "stream": self.processing_streams[stream_id]
                }
            else:
                return {
                    "success": True,
                    "total_streams": len(self.processing_streams),
                    "active_streams": len([s for s in self.processing_streams.values() if s.get("active", False)]),
                    "streams": list(self.processing_streams.keys())
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get stream status: {e}")
            return {
                "success": False,
                "error": f"Status retrieval failed: {str(e)}"
            }
    
    def get_recent_events(
        self, 
        limit: int = 100, 
        event_type: IntelligenceEventType = None
    ) -> Dict[str, Any]:
        """Get recent intelligence events"""
        try:
            events = list(self.intelligence_cache.values())
            
            # Filter by event type if specified
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda e: e.timestamp, reverse=True)
            
            # Limit results
            events = events[:limit]
            
            # Convert to dict for JSON serialization
            event_dicts = []
            for event in events:
                event_dicts.append({
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "timestamp": event.timestamp.isoformat(),
                    "document_id": event.document_id,
                    "filename": event.filename,
                    "data": event.data,
                    "priority": event.priority,
                    "requires_attention": event.requires_attention
                })
            
            return {
                "success": True,
                "total_events": len(event_dicts),
                "events": event_dicts
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent events: {e}")
            return {
                "success": False,
                "error": f"Event retrieval failed: {str(e)}"
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        return {
            "service_name": "RealTimeIntelligenceService",
            "active_streams": len([s for s in self.processing_streams.values() if s.get("active", False)]),
            "total_streams": len(self.processing_streams),
            "total_events": len(self.intelligence_cache),
            "active_subscribers": len(self.subscribers),
            "events_queue_size": self.events_queue.qsize(),
            "capabilities": {
                "real_time_processing": True,
                "stream_management": True,
                "event_system": True,
                "alert_generation": True,
                "insight_discovery": True
            },
            "timestamp": datetime.now().isoformat()
        }
