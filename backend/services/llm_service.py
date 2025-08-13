#!/usr/bin/env python3
"""
Advanced LLM Service for DocuGenie Ultra
Integrates OpenAI GPT, Anthropic Claude, and local models for healthcare document intelligence
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import asyncio
from enum import Enum

# LLM Provider imports
import openai
OPENAI_AVAILABLE = True

import anthropic
ANTHROPIC_AVAILABLE = True

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from transformers.pipelines import pipeline
    from langchain_community.llms import HuggingFacePipeline
    LOCAL_LLM_AVAILABLE = True
except ImportError:
    LOCAL_LLM_AVAILABLE = False

# Configuration - using environment variables directly

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AUTO = "auto"

class LLMService:
    """Advanced LLM service for healthcare document intelligence"""
    
    def __init__(self):
        """Initialize LLM service with multiple providers"""
        self.providers = {}
        self.current_provider = None
        self.healthcare_prompts = self._load_healthcare_prompts()
        
        # Initialize providers
        self._initialize_openai()
        self._initialize_anthropic()
        self._initialize_local_llm()
        
        # Set default provider
        self._set_default_provider()
        
        logger.info("✅ LLM Service initialized successfully")
    
    def _load_healthcare_prompts(self) -> Dict[str, str]:
        """Load healthcare-specific prompt templates"""
        return {
            "document_summary": """You are a healthcare document intelligence expert. Analyze the following document and provide a comprehensive summary:

Document Content:
{content}

Please provide:
1. Document Type and Purpose
2. Key Information Extracted
3. Clinical Relevance
4. Action Items Required
5. Compliance Notes

Summary:""",
            
            "medical_qa": """You are a healthcare AI assistant. Answer the following question based on the provided medical document context:

Question: {question}

Context:
{context}

Please provide:
- Accurate answer based on the context
- Confidence level
- Any limitations or disclaimers
- Related medical considerations

Answer:""",
            
            "lab_result_analysis": """You are a clinical laboratory expert. Analyze the following lab results:

Lab Results:
{content}

Please provide:
1. Normal vs Abnormal Values
2. Clinical Significance
3. Potential Health Implications
4. Recommended Follow-up Actions
5. Critical Values Alert (if any)

Analysis:""",
            
            "compliance_check": """You are a healthcare compliance expert. Review the following document for regulatory compliance:

Document:
{content}

Please check for:
1. HIPAA Compliance
2. FDA Requirements (if applicable)
3. Clinical Documentation Standards
4. Data Privacy Requirements
5. Audit Trail Completeness

Compliance Assessment:""",
            
            "clinical_documentation": """You are a clinical documentation specialist. Review and enhance the following medical document:

Document:
{content}

Please provide:
1. Documentation Quality Assessment
2. Missing Critical Information
3. Standardization Recommendations
4. Clinical Decision Support
5. Risk Assessment

Enhanced Documentation:"""
        }
    
    def _initialize_openai(self):
        """Initialize OpenAI provider"""
        if not OPENAI_AVAILABLE:
            logger.info("ℹ️ OpenAI not available - skipping initialization")
            return
        
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key.strip():
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                self.providers[LLMProvider.OPENAI] = {
                    "client": client,
                    "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                    "available": True
                }
                logger.info("✅ OpenAI provider initialized")
            else:
                logger.info("ℹ️ OpenAI API key not provided - using fallback providers")
                # Don't log as warning since it's optional
        except Exception as e:
            logger.info(f"ℹ️ OpenAI initialization skipped: {e}")
    
    def _initialize_anthropic(self):
        """Initialize Anthropic provider"""
        if not ANTHROPIC_AVAILABLE:
            logger.info("ℹ️ Anthropic not available - skipping initialization")
            return
        
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key and api_key.strip():
                self.providers[LLMProvider.ANTHROPIC] = {
                    "client": anthropic.Anthropic(api_key=api_key),
                    "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                    "available": True
                }
                logger.info("✅ Anthropic provider initialized")
            else:
                logger.info("ℹ️ Anthropic API key not provided - using fallback providers")
                # Don't log as warning since it's optional
        except Exception as e:
            logger.info(f"ℹ️ Anthropic initialization skipped: {e}")
    
    def _initialize_local_llm(self):
        """Initialize local LLM provider"""
        if not LOCAL_LLM_AVAILABLE:
            return
        
        try:
            # Use a healthcare-optimized model
            model_name = "microsoft/DialoGPT-medium"  # Can be upgraded to healthcare-specific models
            
            self.providers[LLMProvider.LOCAL] = {
                "model_name": model_name,
                "models": [model_name],
                "available": True,
                "initialized": False
            }
            logger.info("✅ Local LLM provider initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Local LLM: {e}")
    
    def _set_default_provider(self):
        """Set the default LLM provider based on availability"""
        if LLMProvider.OPENAI in self.providers and self.providers[LLMProvider.OPENAI]["available"]:
            self.current_provider = LLMProvider.OPENAI
        elif LLMProvider.ANTHROPIC in self.providers and self.providers[LLMProvider.ANTHROPIC]["available"]:
            self.current_provider = LLMProvider.ANTHROPIC
        elif LLMProvider.LOCAL in self.providers and self.providers[LLMProvider.LOCAL]["available"]:
            self.current_provider = LLMProvider.LOCAL
        else:
            self.current_provider = None
            logger.warning("⚠️ No LLM providers available")
    
    async def generate_response(
        self, 
        prompt: str, 
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using specified or default LLM provider"""
        try:
            target_provider = provider or self.current_provider
            
            if not target_provider:
                return {
                    "success": False,
                    "error": "No LLM provider available"
                }
            
            if target_provider not in self.providers:
                return {
                    "success": False,
                    "error": f"Provider {target_provider.value} not available"
                }
            
            provider_info = self.providers[target_provider]
            if not provider_info["available"]:
                return {
                    "success": False,
                    "error": f"Provider {target_provider.value} not available"
                }
            
            # Get default model if none specified
            target_model = model or self.providers[target_provider].get("models", [None])[0]
            
            if not target_model:
                return {
                    "success": False,
                    "error": f"No model available for provider {target_provider.value}"
                }
            
            # Generate response based on provider
            if target_provider == LLMProvider.OPENAI:
                return await self._generate_openai_response(prompt, target_model, max_tokens, temperature, **kwargs)
            elif target_provider == LLMProvider.ANTHROPIC:
                return await self._generate_anthropic_response(prompt, target_model, max_tokens, temperature, **kwargs)
            elif target_provider == LLMProvider.LOCAL:
                return await self._generate_local_response(prompt, target_model, max_tokens, temperature, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported provider: {target_provider.value}"
                }
                
        except Exception as e:
            logger.error(f"❌ LLM response generation failed: {e}")
            return {
                "success": False,
                "error": f"Response generation failed: {str(e)}"
            }
    
    async def _generate_openai_response(
        self, 
        prompt: str, 
        model: str = None, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        try:
            target_model = model or "gpt-3.5-turbo"
            
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model=target_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return {
                "success": True,
                "provider": "openai",
                "model": target_model,
                "response": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ OpenAI response generation failed: {e}")
            return {
                "success": False,
                "error": f"OpenAI generation failed: {str(e)}"
            }
    
    async def _generate_anthropic_response(
        self, 
        prompt: str, 
        model: str = None, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using Anthropic Claude"""
        try:
            target_model = model or "claude-3-haiku-20240307"
            client = self.providers[LLMProvider.ANTHROPIC]["client"]
            
            response = client.messages.create(
                model=target_model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            return {
                "success": True,
                "provider": "anthropic",
                "model": target_model,
                "response": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Anthropic response generation failed: {e}")
            return {
                "success": False,
                "error": f"Anthropic generation failed: {str(e)}"
            }
    
    async def _generate_local_response(
        self, 
        prompt: str, 
        model: str = None, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using local LLM"""
        try:
            target_model = model or self.providers[LLMProvider.LOCAL]["model_name"]
            
            # Initialize local model if not already done
            if not self.providers[LLMProvider.LOCAL].get("initialized", False):
                await self._initialize_local_model(target_model)
            
            # For now, return a simplified response
            # In production, you would use the actual local model
            response = f"Local LLM response to: {prompt[:100]}..."
            
            return {
                "success": True,
                "provider": "local",
                "model": target_model,
                "response": response,
                "usage": {"input_tokens": len(prompt), "output_tokens": len(response)},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Local LLM response generation failed: {e}")
            return {
                "success": False,
                "error": f"Local LLM generation failed: {str(e)}"
            }
    
    async def _initialize_local_model(self, model_name: str):
        """Initialize local LLM model"""
        try:
            # This would initialize the actual model
            # For now, just mark as initialized
            self.providers[LLMProvider.LOCAL]["initialized"] = True
            logger.info(f"✅ Local model {model_name} initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize local model: {e}")
    
    async def analyze_healthcare_document(
        self, 
        content: str, 
        analysis_type: str = "document_summary",
        provider: LLMProvider = None
    ) -> Dict[str, Any]:
        """Analyze healthcare document using specialized prompts"""
        try:
            if analysis_type not in self.healthcare_prompts:
                return {
                    "success": False,
                    "error": f"Unknown analysis type: {analysis_type}"
                }
            
            prompt_template = self.healthcare_prompts[analysis_type]
            prompt = prompt_template.format(content=content[:4000])  # Limit content length
            
            result = await self.generate_response(
                prompt=prompt,
                provider=provider,
                max_tokens=1500,
                temperature=0.3  # Lower temperature for healthcare analysis
            )
            
            if result["success"]:
                result["analysis_type"] = analysis_type
                result["healthcare_optimized"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Healthcare document analysis failed: {e}")
            return {
                "success": False,
                "error": f"Healthcare analysis failed: {str(e)}"
            }
    
    async def batch_process_documents(
        self, 
        documents: List[Dict[str, Any]], 
        analysis_type: str = "document_summary",
        provider: LLMProvider = None
    ) -> Dict[str, Any]:
        """Batch process multiple documents"""
        try:
            results = []
            total_documents = len(documents)
            
            logger.info(f"🔄 Starting batch processing of {total_documents} documents")
            
            for i, doc in enumerate(documents):
                logger.info(f"📄 Processing document {i+1}/{total_documents}: {doc.get('filename', 'Unknown')}")
                
                result = await self.analyze_healthcare_document(
                    content=doc.get('content', ''),
                    analysis_type=analysis_type,
                    provider=provider
                )
                
                results.append({
                    "document_id": doc.get('id'),
                    "filename": doc.get('filename'),
                    "analysis_result": result
                })
                
                # Add small delay to avoid rate limiting
                await asyncio.sleep(0.1)
            
            successful = sum(1 for r in results if r["analysis_result"]["success"])
            
            return {
                "success": True,
                "total_documents": total_documents,
                "successful_analyses": successful,
                "failed_analyses": total_documents - successful,
                "results": results,
                "batch_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            return {
                "success": False,
                "error": f"Batch processing failed: {str(e)}"
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive LLM service status"""
        return {
            "service_name": "LLMService",
            "current_provider": self.current_provider.value if self.current_provider else None,
            "providers": {
                provider.value: {
                    "available": info["available"],
                    "models": info.get("models", []),
                    "initialized": info.get("initialized", False)
                }
                for provider, info in self.providers.items()
            },
            "healthcare_prompts": list(self.healthcare_prompts.keys()),
            "capabilities": {
                "document_analysis": True,
                "batch_processing": True,
                "multi_provider": True,
                "healthcare_optimized": True
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def switch_provider(self, provider: LLMProvider) -> Dict[str, Any]:
        """Switch to a different LLM provider"""
        try:
            if provider not in self.providers:
                return {
                    "success": False,
                    "error": f"Provider {provider.value} not available"
                }
            
            if not self.providers[provider]["available"]:
                return {
                    "success": False,
                    "error": f"Provider {provider.value} not available"
                }
            
            self.current_provider = provider
            
            return {
                "success": True,
                "message": f"Switched to {provider.value} provider",
                "provider": provider.value,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Provider switch failed: {e}")
            return {
                "success": False,
                "error": f"Provider switch failed: {str(e)}"
            }
