"""
Advanced Search Service with OpenSearch and Qdrant integration
Provides real search capabilities for documents and content
"""
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# OpenSearch imports
try:
    from opensearchpy import OpenSearch, helpers
    OPENSEARCH_AVAILABLE = True
except ImportError:
    OPENSEARCH_AVAILABLE = False
    print("⚠️ OpenSearch not available. Please install: pip install opensearch-py")

# Qdrant imports
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Range
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("⚠️ Qdrant not available. Please install: pip install qdrant-client")

# Sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ Sentence Transformers not available. Please install: pip install sentence-transformers")

from core.config import settings

logger = logging.getLogger(__name__)

class SearchService:
    """Advanced search service with multiple search engines"""
    
    def __init__(self):
        """Initialize search service with available engines"""
        self.opensearch_client = None
        self.qdrant_client = None
        self.embedding_model = None
        
        # Service availability
        self.opensearch_available = OPENSEARCH_AVAILABLE
        self.qdrant_available = QDRANT_AVAILABLE
        self.embeddings_available = SENTENCE_TRANSFORMERS_AVAILABLE
        
        # Initialize OpenSearch
        if self.opensearch_available:
            try:
                self.opensearch_client = OpenSearch(
                    hosts=[os.getenv("OPENSEARCH_HOST", "localhost:9200")],
                    http_auth=(os.getenv("OPENSEARCH_USER", "admin"), 
                              os.getenv("OPENSEARCH_PASSWORD", "admin")),
                    use_ssl=os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true",
                    verify_certs=False,
                    ssl_show_warn=False
                )
                
                # Ensure index exists
                self._ensure_opensearch_index()
                logger.info("✅ OpenSearch search service initialized successfully")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenSearch: {e}")
                self.opensearch_client = None
                self.opensearch_available = False
        
        # Initialize Qdrant
        if self.qdrant_available:
            try:
                self.qdrant_client = QdrantClient(
                    host=os.getenv("QDRANT_HOST", "localhost"),
                    port=int(os.getenv("QDRANT_PORT", "6333"))
                )
                
                # Ensure collection exists
                self._ensure_qdrant_collection()
                logger.info("✅ Qdrant vector search service initialized successfully")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize Qdrant: {e}")
                self.qdrant_client = None
                self.qdrant_available = False
        
        # Initialize embedding model
        if self.embeddings_available:
            try:
                model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
                self.embedding_model = SentenceTransformer(model_name)
                logger.info(f"✅ Embedding model loaded: {model_name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to load embedding model: {e}")
                self.embedding_model = None
                self.embeddings_available = False
        
        if not any([self.opensearch_available, self.qdrant_available]):
            logger.warning("⚠️ No search engines available. Using basic text search only.")
    
    def _ensure_opensearch_index(self):
        """Ensure OpenSearch index exists with proper mapping"""
        try:
            index_name = "docugenie_documents"
            
            if not self.opensearch_client.indices.exists(index=index_name):
                # Create index with mapping
                mapping = {
                    "mappings": {
                        "properties": {
                            "document_id": {"type": "keyword"},
                            "filename": {"type": "text", "analyzer": "standard"},
                            "content": {"type": "text", "analyzer": "standard"},
                            "document_type": {"type": "keyword"},
                            "patient_id": {"type": "keyword"},
                            "provider_id": {"type": "keyword"},
                            "uploaded_at": {"type": "date"},
                            "processing_method": {"type": "keyword"},
                            "ai_models": {"type": "keyword"},
                            "entities": {"type": "keyword"},
                            "summary": {"type": "text", "analyzer": "standard"},
                            "tags": {"type": "keyword"},
                            "confidence": {"type": "float"}
                        }
                    },
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "analysis": {
                            "analyzer": {
                                "healthcare_analyzer": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": ["lowercase", "stop", "snowball"]
                                }
                            }
                        }
                    }
                }
                
                self.opensearch_client.indices.create(index=index_name, body=mapping)
                logger.info(f"✅ Created OpenSearch index: {index_name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to create OpenSearch index: {e}")
    
    def _ensure_qdrant_collection(self):
        """Ensure Qdrant collection exists"""
        try:
            collection_name = "docugenie_vectors"
            
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if collection_name not in collection_names:
                # Create collection
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)  # all-MiniLM-L6-v2 size
                )
                logger.info(f"✅ Created Qdrant collection: {collection_name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to create Qdrant collection: {e}")
    
    def index_document(self, document_data: Dict) -> Dict:
        """
        Index a document for search
        
        Args:
            document_data: Document data to index
            
        Returns:
            Dict containing indexing results
        """
        try:
            results = {}
            
            # Index in OpenSearch
            if self.opensearch_available and self.opensearch_client:
                opensearch_result = self._index_in_opensearch(document_data)
                results["opensearch"] = opensearch_result
            
            # Index in Qdrant
            if self.qdrant_available and self.qdrant_client and self.embeddings_available:
                qdrant_result = self._index_in_qdrant(document_data)
                results["qdrant"] = qdrant_result
            
            return {
                "success": True,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _index_in_opensearch(self, document_data: Dict) -> Dict:
        """Index document in OpenSearch"""
        try:
            index_name = "docugenie_documents"
            
            # Prepare document for indexing
            doc_body = {
                "document_id": document_data.get("id"),
                "filename": document_data.get("filename"),
                "content": document_data.get("extracted_text", ""),
                "document_type": document_data.get("document_type"),
                "patient_id": document_data.get("patient_id"),
                "provider_id": document_data.get("provider_id"),
                "uploaded_at": document_data.get("uploaded_at"),
                "processing_method": document_data.get("processing_method"),
                "ai_models": document_data.get("ai_models_used", []),
                "entities": document_data.get("entities_extracted", []),
                "summary": document_data.get("summary", ""),
                "tags": document_data.get("tags", []),
                "confidence": document_data.get("processing_confidence", 0.0),
                "indexed_at": datetime.utcnow().isoformat()
            }
            
            # Index document
            response = self.opensearch_client.index(
                index=index_name,
                body=doc_body,
                id=document_data.get("id")
            )
            
            return {
                "success": True,
                "result": response.get("result"),
                "document_id": document_data.get("id")
            }
            
        except Exception as e:
            logger.error(f"OpenSearch indexing error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _index_in_qdrant(self, document_data: Dict) -> Dict:
        """Index document in Qdrant for vector search"""
        try:
            collection_name = "docugenie_vectors"
            
            # Generate embedding for content
            content = document_data.get("extracted_text", "")
            if not content:
                return {"success": False, "error": "No content to embed"}
            
            # Create embedding
            embedding = self.embedding_model.encode(content)
            
            # Prepare point for Qdrant
            point = PointStruct(
                id=document_data.get("id"),
                vector=embedding.tolist(),
                payload={
                    "document_id": document_data.get("id"),
                    "filename": document_data.get("filename"),
                    "content_preview": content[:500],
                    "document_type": document_data.get("document_type"),
                    "patient_id": document_data.get("patient_id"),
                    "provider_id": document_data.get("provider_id"),
                    "processing_method": document_data.get("processing_method"),
                    "confidence": document_data.get("processing_confidence", 0.0)
                }
            )
            
            # Upsert point
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            return {
                "success": True,
                "document_id": document_data.get("id"),
                "vector_size": len(embedding)
            }
            
        except Exception as e:
            logger.error(f"Qdrant indexing error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_documents(self, query: str, search_type: str = "hybrid", filters: Dict = None, limit: int = 20) -> Dict:
        """
        Search documents using available search engines
        
        Args:
            query: Search query
            search_type: Type of search (text, vector, hybrid)
            filters: Search filters
            limit: Maximum results to return
            
        Returns:
            Dict containing search results
        """
        try:
            results = {}
            
            # Text search with OpenSearch
            if self.opensearch_available and self.opensearch_client:
                text_results = self._search_opensearch(query, filters, limit)
                results["text_search"] = text_results
            
            # Vector search with Qdrant
            if self.qdrant_available and self.qdrant_client and self.embeddings_available:
                vector_results = self._search_qdrant(query, filters, limit)
                results["vector_search"] = vector_results
            
            # Hybrid search (combine results)
            if search_type == "hybrid" and results:
                hybrid_results = self._combine_search_results(results, limit)
                results["hybrid_search"] = hybrid_results
            
            return {
                "success": True,
                "query": query,
                "search_type": search_type,
                "total_results": len(results.get("hybrid_search", results.get("text_search", []))),
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def _search_opensearch(self, query: str, filters: Dict = None, limit: int = 20) -> List[Dict]:
        """Search documents in OpenSearch"""
        try:
            index_name = "docugenie_documents"
            
            # Build search query
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["filename^2", "content", "summary^1.5"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ]
                    }
                },
                "size": limit,
                "highlight": {
                    "fields": {
                        "content": {},
                        "summary": {}
                    }
                }
            }
            
            # Add filters
            if filters:
                filter_conditions = []
                
                if filters.get("document_type"):
                    filter_conditions.append({
                        "term": {"document_type": filters["document_type"]}
                    })
                
                if filters.get("patient_id"):
                    filter_conditions.append({
                        "term": {"patient_id": filters["patient_id"]}
                    })
                
                if filters.get("date_range"):
                    filter_conditions.append({
                        "range": {
                            "uploaded_at": {
                                "gte": filters["date_range"]["start"],
                                "lte": filters["date_range"]["end"]
                            }
                        }
                    })
                
                if filter_conditions:
                    search_body["query"]["bool"]["filter"] = filter_conditions
            
            # Execute search
            response = self.opensearch_client.search(
                index=index_name,
                body=search_body
            )
            
            # Process results
            results = []
            for hit in response["hits"]["hits"]:
                result = {
                    "document_id": hit["_id"],
                    "score": hit["_score"],
                    "source": hit["_source"],
                    "highlights": hit.get("highlight", {})
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"OpenSearch search error: {e}")
            return []
    
    def _search_qdrant(self, query: str, filters: Dict = None, limit: int = 20) -> List[Dict]:
        """Search documents in Qdrant using vector similarity"""
        try:
            collection_name = "docugenie_vectors"
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Build filter
            qdrant_filter = None
            if filters:
                filter_conditions = []
                
                if filters.get("document_type"):
                    filter_conditions.append(
                        FieldCondition(key="document_type", match={"value": filters["document_type"]})
                    )
                
                if filters.get("patient_id"):
                    filter_conditions.append(
                        FieldCondition(key="patient_id", match={"value": filters["patient_id"]})
                    )
                
                if filter_conditions:
                    qdrant_filter = Filter(must=filter_conditions)
            
            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding.tolist(),
                query_filter=qdrant_filter,
                limit=limit,
                with_payload=True
            )
            
            # Process results
            results = []
            for point in search_result:
                result = {
                    "document_id": point.id,
                    "score": point.score,
                    "payload": point.payload
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            return []
    
    def _combine_search_results(self, search_results: Dict, limit: int = 20) -> List[Dict]:
        """Combine results from different search engines"""
        try:
            all_results = []
            
            # Collect all results with source information
            for engine, results in search_results.items():
                if isinstance(results, list):
                    for result in results:
                        result_copy = result.copy()
                        result_copy["search_engine"] = engine
                        all_results.append(result_copy)
            
            # Sort by score (higher is better)
            all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            # Remove duplicates based on document_id
            seen_ids = set()
            unique_results = []
            
            for result in all_results:
                doc_id = result.get("document_id")
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    unique_results.append(result)
                    
                    if len(unique_results) >= limit:
                        break
            
            return unique_results
            
        except Exception as e:
            logger.error(f"Error combining search results: {e}")
            return []
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query"""
        try:
            suggestions = []
            
            if self.opensearch_available and self.opensearch_client:
                # Use OpenSearch suggest API
                suggest_body = {
                    "suggest": {
                        "filename_suggest": {
                            "prefix": partial_query,
                            "completion": {
                                "field": "filename_suggest",
                                "size": limit
                            }
                        }
                    }
                }
                
                # This would require a completion field in the mapping
                # For now, return basic suggestions
                suggestions = [f"{partial_query} document", f"{partial_query} report"]
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []
    
    def get_search_analytics(self) -> Dict:
        """Get search analytics and statistics"""
        try:
            analytics = {
                "total_indexed_documents": 0,
                "search_engines": {
                    "opensearch": self.opensearch_available,
                    "qdrant": self.qdrant_available,
                    "embeddings": self.embeddings_available
                },
                "indexes": {},
                "collections": {}
            }
            
            # Get OpenSearch stats
            if self.opensearch_available and self.opensearch_client:
                try:
                    index_name = "docugenie_documents"
                    stats = self.opensearch_client.indices.stats(index=index_name)
                    analytics["indexes"]["opensearch"] = {
                        "name": index_name,
                        "document_count": stats["indices"][index_name]["total"]["docs"]["count"]
                    }
                except Exception as e:
                    logger.warning(f"Could not get OpenSearch stats: {e}")
            
            # Get Qdrant stats
            if self.qdrant_available and self.qdrant_client:
                try:
                    collection_name = "docugenie_vectors"
                    collection_info = self.qdrant_client.get_collection(collection_name)
                    analytics["collections"]["qdrant"] = {
                        "name": collection_name,
                        "vector_count": collection_info.points_count
                    }
                except Exception as e:
                    logger.warning(f"Could not get Qdrant stats: {e}")
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting search analytics: {e}")
            return {"error": str(e)}
    
    def get_service_status(self) -> Dict:
        """Get search service status"""
        return {
            "service_name": "SearchService",
            "opensearch_available": self.opensearch_available,
            "qdrant_available": self.qdrant_available,
            "embeddings_available": self.embeddings_available,
            "search_capabilities": {
                "text_search": self.opensearch_available,
                "vector_search": self.qdrant_available and self.embeddings_available,
                "hybrid_search": self.opensearch_available and self.qdrant_available,
                "semantic_search": self.embeddings_available,
                "faceted_search": self.opensearch_available
            },
            "analytics": self.get_search_analytics()
        }
