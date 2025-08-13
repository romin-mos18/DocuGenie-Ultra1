#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) Service
Integrates Docling with LangChain for advanced document search and AI-powered Q&A
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# LangChain imports
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import TextLoader
    from langchain_community.vectorstores import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain not available. Please install: pip install langchain langchain-community")

# Docling service import
from services.docling_service import DoclingService

logger = logging.getLogger(__name__)

class RAGService:
    """RAG service for advanced document search and AI-powered Q&A"""
    
    def __init__(self):
        """Initialize RAG service with Docling and LangChain integration"""
        self.docling_service = DoclingService()
        self.langchain_available = LANGCHAIN_AVAILABLE
        
        # Initialize components
        self.text_splitter = None
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
        
        # Initialize if LangChain is available
        if self.langchain_available:
            self._initialize_langchain_components()
        
        # Document storage
        self.processed_documents = {}
        self.document_chunks = {}
        
        logger.info("✅ RAG Service initialized successfully")
    
    def _initialize_langchain_components(self):
        """Initialize LangChain components for RAG pipeline"""
        try:
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # Initialize embeddings (using sentence-transformers)
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            logger.info("✅ LangChain components initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LangChain components: {e}")
            self.langchain_available = False
    
    def process_document_for_rag(self, file_path: str, file_type: str) -> Dict:
        """Process document and prepare it for RAG pipeline"""
        try:
            logger.info(f"🔄 Processing document for RAG: {file_path}")
            
            # Process document with Docling
            docling_result = self.docling_service.process_document(file_path, file_type)
            
            if not docling_result["success"]:
                return {
                    "success": False,
                    "error": f"Docling processing failed: {docling_result.get('error', 'Unknown error')}"
                }
            
            # Extract text content
            text_content = docling_result["text"]
            
            if not text_content or len(text_content.strip()) == 0:
                return {
                    "success": False,
                    "error": "No text content extracted from document"
                }
            
            # Split text into chunks
            chunks = self._split_text_into_chunks(text_content)
            
            # Store document information
            doc_id = os.path.basename(file_path)
            self.processed_documents[doc_id] = {
                "file_path": file_path,
                "file_type": file_type,
                "processing_method": docling_result["processing_method"],
                "confidence": docling_result["confidence"],
                "word_count": docling_result["word_count"],
                "chunk_count": len(chunks),
                "processed_at": datetime.now().isoformat()
            }
            
            self.document_chunks[doc_id] = chunks
            
            # Update vector store if available
            if self.langchain_available and chunks:
                self._update_vector_store(doc_id, chunks)
            
            return {
                "success": True,
                "document_id": doc_id,
                "chunks_created": len(chunks),
                "total_words": docling_result["word_count"],
                "processing_method": docling_result["processing_method"],
                "message": "Document processed and prepared for RAG pipeline"
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing document for RAG: {e}")
            return {
                "success": False,
                "error": f"RAG processing failed: {str(e)}"
            }
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into manageable chunks for processing"""
        if not self.text_splitter:
            # Fallback: simple splitting
            words = text.split()
            chunk_size = 1000
            chunks = []
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                chunks.append(chunk)
            
            return chunks
        
        try:
            # Use LangChain text splitter
            chunks = self.text_splitter.split_text(text)
            return chunks
        except Exception as e:
            logger.warning(f"LangChain text splitting failed, using fallback: {e}")
            # Fallback: simple splitting
            words = text.split()
            chunk_size = 1000
            chunks = []
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                chunks.append(chunk)
            
            return chunks
    
    def _update_vector_store(self, doc_id: str, chunks: List[str]):
        """Update vector store with new document chunks"""
        try:
            if not self.embeddings:
                logger.warning("Embeddings not available, skipping vector store update")
                return
            
            # Create documents for vector store
            from langchain.schema import Document
            
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "document_id": doc_id,
                        "chunk_index": i,
                        "chunk_size": len(chunk),
                        "source": doc_id
                    }
                )
                documents.append(doc)
            
            # Create or update vector store
            if not self.vectorstore:
                # Create new vector store
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    collection_name="docugenie_documents"
                )
                self.retriever = self.vectorstore.as_retriever(
                    search_kwargs={"k": 5}
                )
                logger.info("✅ Vector store created successfully")
            else:
                # Add to existing vector store
                self.vectorstore.add_documents(documents)
                logger.info(f"✅ Added {len(documents)} chunks to vector store")
                
        except Exception as e:
            logger.error(f"❌ Failed to update vector store: {e}")
    
    def search_documents(self, query: str, limit: int = 5) -> Dict:
        """Search documents using semantic similarity"""
        try:
            if not self.langchain_available:
                return {
                    "success": False,
                    "error": "LangChain not available for semantic search"
                }
            
            if not self.vectorstore:
                return {
                    "success": False,
                    "error": "No documents processed yet. Please process documents first."
                }
            
            # Perform semantic search
            results = self.retriever.get_relevant_documents(query)
            
            # Format results
            search_results = []
            for i, doc in enumerate(results[:limit]):
                search_results.append({
                    "rank": i + 1,
                    "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": 0.9 - (i * 0.1)  # Simple ranking
                })
            
            return {
                "success": True,
                "query": query,
                "results": search_results,
                "total_results": len(search_results),
                "search_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return {
                "success": False,
                "error": f"Search failed: {str(e)}"
            }
    
    def answer_question(self, question: str, context_limit: int = 3) -> Dict:
        """Answer questions using RAG pipeline"""
        try:
            if not self.langchain_available:
                return {
                    "success": False,
                    "error": "LangChain not available for Q&A"
                }
            
            if not self.vectorstore:
                return {
                    "success": False,
                    "error": "No documents processed yet. Please process documents first."
                }
            
            # Retrieve relevant context
            relevant_docs = self.retriever.get_relevant_documents(question)
            
            if not relevant_docs:
                return {
                    "success": False,
                    "error": "No relevant documents found to answer the question"
                }
            
            # Create context from relevant documents
            context = "\n\n".join([doc.page_content for doc in relevant_docs[:context_limit]])
            
            # Create a simple Q&A response (in production, you'd use an LLM)
            answer = self._generate_answer_from_context(question, context)
            
            return {
                "success": True,
                "question": question,
                "answer": answer,
                "context_sources": [doc.metadata.get("document_id", "Unknown") for doc in relevant_docs[:context_limit]],
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Q&A failed: {e}")
            return {
                "success": False,
                "error": f"Q&A failed: {str(e)}"
            }
    
    def _generate_answer_from_context(self, question: str, context: str) -> str:
        """Generate answer from context (simplified version)"""
        # This is a simplified answer generation
        # In production, you would use an actual LLM like OpenAI GPT, Anthropic Claude, etc.
        
        question_lower = question.lower()
        context_lower = context.lower()
        
        # Simple keyword-based answer generation
        if "how" in question_lower:
            return f"Based on the document content, here's how to proceed: {context[:200]}..."
        elif "what" in question_lower:
            return f"The document contains the following information: {context[:200]}..."
        elif "when" in question_lower:
            return f"According to the document: {context[:200]}..."
        else:
            return f"Based on the available context: {context[:200]}..."
    
    def get_rag_status(self) -> Dict:
        """Get RAG service status and statistics"""
        return {
            "service_name": "RAGService",
            "langchain_available": self.langchain_available,
            "docling_available": self.docling_service.docling_available,
            "vector_store_ready": self.vectorstore is not None,
            "documents_processed": len(self.processed_documents),
            "total_chunks": sum(len(chunks) for chunks in self.document_chunks.values()),
            "capabilities": {
                "document_processing": True,
                "semantic_search": self.langchain_available,
                "question_answering": self.langchain_available,
                "vector_embeddings": self.langchain_available
            },
            "ai_models": {
                "docling": ["DocLayNet", "TableFormer"],
                "embeddings": "sentence-transformers/all-MiniLM-L6-v2" if self.embeddings else "Not available"
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def get_document_summary(self, document_id: str) -> Dict:
        """Get summary of a processed document"""
        if document_id not in self.processed_documents:
            return {
                "success": False,
                "error": "Document not found"
            }
        
        doc_info = self.processed_documents[document_id]
        chunks = self.document_chunks.get(document_id, [])
        
        return {
            "success": True,
            "document_id": document_id,
            "file_path": doc_info["file_path"],
            "file_type": doc_info["file_type"],
            "processing_method": doc_info["processing_method"],
            "confidence": doc_info["confidence"],
            "word_count": doc_info["word_count"],
            "chunk_count": doc_info["chunk_count"],
            "chunks_preview": [chunk[:100] + "..." if len(chunk) > 100 else chunk for chunk in chunks[:3]],
            "processed_at": doc_info["processed_at"]
        }
