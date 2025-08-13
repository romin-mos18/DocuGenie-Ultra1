#!/usr/bin/env python3
"""
Healthcare Model Training Service
Trains custom models for medical document analysis, lab result interpretation, and clinical decision support
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import asyncio
from pathlib import Path
import pickle
from enum import Enum

# ML/AI imports
try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, accuracy_score
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML libraries not available. Please install: pip install scikit-learn pandas numpy joblib")

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    from transformers import AutoTokenizer, AutoModel, TrainingArguments, Trainer
    DEEP_LEARNING_AVAILABLE = True
except ImportError:
    DEEP_LEARNING_AVAILABLE = False
    print("⚠️ Deep learning libraries not available. Please install: pip install torch transformers")

from core.config import settings

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Supported model types"""
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    SUMMARIZATION = "summarization"
    COMPLIANCE = "compliance"
    CLINICAL_DECISION = "clinical_decision"

class HealthcareModelService:
    """Service for training custom healthcare models"""
    
    def __init__(self):
        """Initialize healthcare model training service"""
        self.models_dir = Path("./models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.trained_models = {}
        self.training_datasets = {}
        self.model_metadata = {}
        
        # Load existing models
        self._load_existing_models()
        
        # Initialize ML capabilities
        self.ml_available = ML_AVAILABLE
        self.deep_learning_available = DEEP_LEARNING_AVAILABLE
        
        logger.info("✅ Healthcare Model Service initialized successfully")
    
    def _load_existing_models(self):
        """Load existing trained models from disk"""
        try:
            for model_file in self.models_dir.glob("*.pkl"):
                try:
                    model_name = model_file.stem
                    with open(model_file, 'rb') as f:
                        model_data = pickle.load(f)
                    
                    self.trained_models[model_name] = model_data
                    logger.info(f"✅ Loaded existing model: {model_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load model {model_file}: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to load existing models: {e}")
    
    def create_training_dataset(
        self, 
        name: str, 
        documents: List[Dict[str, Any]], 
        labels: List[str],
        model_type: ModelType
    ) -> Dict[str, Any]:
        """Create a training dataset from documents"""
        try:
            if not self.ml_available:
                return {
                    "success": False,
                    "error": "ML libraries not available"
                }
            
            # Validate input
            if len(documents) != len(labels):
                return {
                    "success": False,
                    "error": "Number of documents and labels must match"
                }
            
            # Create dataset structure
            dataset = {
                "name": name,
                "model_type": model_type.value,
                "documents": documents,
                "labels": labels,
                "created_at": datetime.now().isoformat(),
                "total_samples": len(documents),
                "unique_labels": list(set(labels)),
                "label_distribution": {}
            }
            
            # Calculate label distribution
            for label in labels:
                dataset["label_distribution"][label] = labels.count(label)
            
            # Store dataset
            self.training_datasets[name] = dataset
            
            # Save to disk
            dataset_file = self.models_dir / f"{name}_dataset.json"
            with open(dataset_file, 'w') as f:
                json.dump(dataset, f, indent=2)
            
            logger.info(f"✅ Created training dataset: {name} with {len(documents)} samples")
            
            return {
                "success": True,
                "dataset_name": name,
                "total_samples": len(documents),
                "unique_labels": len(set(labels)),
                "label_distribution": dataset["label_distribution"]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create training dataset: {e}")
            return {
                "success": False,
                "error": f"Dataset creation failed: {str(e)}"
            }
    
    def train_classification_model(
        self, 
        dataset_name: str, 
        model_name: str,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """Train a classification model for healthcare documents"""
        try:
            if not self.ml_available:
                return {
                    "success": False,
                    "error": "ML libraries not available"
                }
            
            if dataset_name not in self.training_datasets:
                return {
                    "success": False,
                    "error": f"Dataset {dataset_name} not found"
                }
            
            dataset = self.training_datasets[dataset_name]
            
            # Prepare data
            texts = [doc.get('content', '') for doc in dataset['documents']]
            labels = dataset['labels']
            
            # Vectorize text
            vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            X = vectorizer.fit_transform(texts)
            y = labels
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=100,
                random_state=random_state,
                class_weight='balanced'
            )
            
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            classification_rep = classification_report(y_test, y_pred, output_dict=True)
            
            # Save model
            model_data = {
                "model": model,
                "vectorizer": vectorizer,
                "model_type": "classification",
                "dataset_name": dataset_name,
                "accuracy": accuracy,
                "classification_report": classification_rep,
                "training_date": datetime.now().isoformat(),
                "features": X.shape[1],
                "classes": list(set(labels))
            }
            
            # Save to disk
            model_file = self.models_dir / f"{model_name}.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model_data, f)
            
            # Store in memory
            self.trained_models[model_name] = model_data
            self.model_metadata[model_name] = {
                "type": "classification",
                "accuracy": accuracy,
                "training_date": model_data["training_date"],
                "dataset": dataset_name
            }
            
            logger.info(f"✅ Trained classification model: {model_name} with accuracy: {accuracy:.3f}")
            
            return {
                "success": True,
                "model_name": model_name,
                "accuracy": accuracy,
                "classification_report": classification_rep,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "features": X.shape[1],
                "classes": len(set(labels))
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to train classification model: {e}")
            return {
                "success": False,
                "error": f"Model training failed: {str(e)}"
            }
    
    def train_deep_learning_model(
        self, 
        dataset_name: str, 
        model_name: str,
        base_model: str = "bert-base-uncased",
        epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5
    ) -> Dict[str, Any]:
        """Train a deep learning model for healthcare documents"""
        try:
            if not self.deep_learning_available:
                return {
                    "success": False,
                    "error": "Deep learning libraries not available"
                }
            
            if dataset_name not in self.training_datasets:
                return {
                    "success": False,
                    "error": f"Dataset {dataset_name} not found"
                }
            
            dataset = self.training_datasets[dataset_name]
            
            # This is a simplified implementation
            # In production, you would implement full fine-tuning
            
            logger.info(f"🔄 Deep learning training not fully implemented yet for {model_name}")
            
            return {
                "success": False,
                "error": "Deep learning training not fully implemented yet",
                "note": "This feature requires additional implementation for full BERT fine-tuning"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to train deep learning model: {e}")
            return {
                "success": False,
                "error": f"Deep learning training failed: {str(e)}"
            }
    
    def predict_document_class(
        self, 
        model_name: str, 
        document_content: str
    ) -> Dict[str, Any]:
        """Predict document class using trained model"""
        try:
            if model_name not in self.trained_models:
                return {
                    "success": False,
                    "error": f"Model {model_name} not found"
                }
            
            model_data = self.trained_models[model_name]
            
            if model_data["model_type"] != "classification":
                return {
                    "success": False,
                    "error": f"Model {model_name} is not a classification model"
                }
            
            # Vectorize document
            X = model_data["vectorizer"].transform([document_content])
            
            # Make prediction
            prediction = model_data["model"].predict(X)[0]
            probabilities = model_data["model"].predict_proba(X)[0]
            
            # Get class labels
            classes = model_data["classes"]
            class_probabilities = dict(zip(classes, probabilities))
            
            return {
                "success": True,
                "predicted_class": prediction,
                "confidence": float(max(probabilities)),
                "class_probabilities": class_probabilities,
                "model_name": model_name,
                "model_accuracy": model_data["accuracy"]
            }
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            return {
                "success": False,
                "error": f"Prediction failed: {str(e)}"
            }
    
    def batch_predict_documents(
        self, 
        model_name: str, 
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Batch predict document classes"""
        try:
            results = []
            successful = 0
            
            for doc in documents:
                prediction = self.predict_document_class(
                    model_name, 
                    doc.get('content', '')
                )
                
                if prediction["success"]:
                    successful += 1
                
                results.append({
                    "document_id": doc.get('id'),
                    "filename": doc.get('filename'),
                    "prediction": prediction
                })
            
            return {
                "success": True,
                "total_documents": len(documents),
                "successful_predictions": successful,
                "failed_predictions": len(documents) - successful,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Batch prediction failed: {e}")
            return {
                "success": False,
                "error": f"Batch prediction failed: {str(e)}"
            }
    
    def get_model_performance(self, model_name: str) -> Dict[str, Any]:
        """Get performance metrics for a trained model"""
        try:
            if model_name not in self.trained_models:
                return {
                    "success": False,
                    "error": f"Model {model_name} not found"
                }
            
            model_data = self.trained_models[model_name]
            
            return {
                "success": True,
                "model_name": model_name,
                "model_type": model_data["model_type"],
                "accuracy": model_data["accuracy"],
                "training_date": model_data["training_date"],
                "dataset": model_data["dataset_name"],
                "features": model_data["features"],
                "classes": model_data["classes"],
                "classification_report": model_data["classification_report"]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get model performance: {e}")
            return {
                "success": False,
                "error": f"Performance retrieval failed: {str(e)}"
            }
    
    def list_trained_models(self) -> Dict[str, Any]:
        """List all trained models"""
        try:
            models = []
            
            for name, metadata in self.model_metadata.items():
                models.append({
                    "name": name,
                    "type": metadata["type"],
                    "accuracy": metadata["accuracy"],
                    "training_date": metadata["training_date"],
                    "dataset": metadata["dataset"]
                })
            
            return {
                "success": True,
                "total_models": len(models),
                "models": models
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to list models: {e}")
            return {
                "success": False,
                "error": f"Model listing failed: {str(e)}"
            }
    
    def delete_model(self, model_name: str) -> Dict[str, Any]:
        """Delete a trained model"""
        try:
            if model_name not in self.trained_models:
                return {
                    "success": False,
                    "error": f"Model {model_name} not found"
                }
            
            # Remove from memory
            del self.trained_models[model_name]
            del self.model_metadata[model_name]
            
            # Remove from disk
            model_file = self.models_dir / f"{model_name}.pkl"
            if model_file.exists():
                model_file.unlink()
            
            logger.info(f"✅ Deleted model: {model_name}")
            
            return {
                "success": True,
                "message": f"Model {model_name} deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to delete model: {e}")
            return {
                "success": False,
                "error": f"Model deletion failed: {str(e)}"
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        return {
            "service_name": "HealthcareModelService",
            "ml_available": self.ml_available,
            "deep_learning_available": self.deep_learning_available,
            "total_models": len(self.trained_models),
            "total_datasets": len(self.training_datasets),
            "models_directory": str(self.models_dir),
            "capabilities": {
                "classification_training": self.ml_available,
                "deep_learning_training": self.deep_learning_available,
                "batch_prediction": True,
                "model_management": True
            },
            "timestamp": datetime.now().isoformat()
        }
