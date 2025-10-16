"""
VISH AI - Model Handler
Manages Phi-3 Mini model loading, inference, and version control
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VishModelHandler:
    """Handles Phi-3 model loading, inference, and fine-tuned model management"""
    
    def __init__(self, base_model: str = "microsoft/Phi-3-mini-4k-instruct"):
        self.base_model_name = base_model
        self.model = None
        self.tokenizer = None
        self.current_model_path = None
        self.model_version = "base"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Model metadata
        self.metadata_path = "models/vish-ai-mini/metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict[str, Any]:
        """Load model metadata (version, performance, training stats)"""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return {
            "version": "base",
            "last_updated": None,
            "training_runs": 0,
            "dataset_size": 0,
            "performance_metrics": {}
        }
    
    def _save_metadata(self):
        """Save model metadata"""
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def load_model(self, use_quantization: bool = False):
        """Load Phi-3 model (base or fine-tuned version)"""
        try:
            logger.info(f"Loading Phi-3 model on {self.device}...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model_name,
                trust_remote_code=True
            )
            
            # Configure quantization for free-tier optimization
            if use_quantization and self.device == "cuda":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True
                )
                logger.info("Using 4-bit quantization for memory efficiency")
            else:
                quantization_config = None
            
            # Load base model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                device_map=self.device,
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                quantization_config=quantization_config
            )
            
            # Try to load fine-tuned adapter if available
            fine_tuned_path = "models/vish-ai-mini/latest"
            if os.path.exists(fine_tuned_path):
                logger.info(f"Loading fine-tuned adapter from {fine_tuned_path}...")
                self.model = PeftModel.from_pretrained(self.model, fine_tuned_path)
                self.model_version = self.metadata.get("version", "custom")
                self.current_model_path = fine_tuned_path
                logger.info(f"✅ Loaded fine-tuned model version: {self.model_version}")
            else:
                logger.info("✅ Using base Phi-3 model (no fine-tuning yet)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def generate_response(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate response using Phi-3 model"""
        
        if not self.model or not self.tokenizer:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        try:
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Apply chat template
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Tokenize
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract assistant response
            if "<|assistant|>" in full_response:
                response = full_response.split("<|assistant|>")[-1].strip()
            else:
                response = full_response[len(formatted_prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"
    
    def update_model_version(self, new_version: str, metrics: Dict[str, float]):
        """Update model version and metadata after successful training"""
        self.model_version = new_version
        self.metadata["version"] = new_version
        self.metadata["last_updated"] = datetime.utcnow().isoformat()
        self.metadata["training_runs"] += 1
        self.metadata["performance_metrics"] = metrics
        self._save_metadata()
        logger.info(f"✅ Model updated to version {new_version}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get current model information"""
        return {
            "base_model": self.base_model_name,
            "current_version": self.model_version,
            "device": self.device,
            "fine_tuned": self.current_model_path is not None,
            "metadata": self.metadata
        }


# Global model instance
_model_handler = None


def get_model_handler() -> VishModelHandler:
    """Get or create global model handler instance"""
    global _model_handler
    if _model_handler is None:
        _model_handler = VishModelHandler()
        _model_handler.load_model(use_quantization=False)
    return _model_handler


def reload_model():
    """Reload model (useful after fine-tuning)"""
    global _model_handler
    if _model_handler:
        _model_handler.load_model(use_quantization=False)
        logger.info("Model reloaded successfully")
