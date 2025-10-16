"""
VISH AI - Self-Training Pipeline
Automated LoRA fine-tuning with continuous improvement
"""

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
import os
from datetime import datetime
import logging
from typing import List, Dict, Optional
import json

from app.dataset_manager import get_dataset_manager
from app.model_handler import reload_model, get_model_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VishTrainer:
    """Handles automated LoRA fine-tuning of Phi-3 Mini"""
    
    def __init__(
        self,
        base_model: str = "microsoft/Phi-3-mini-4k-instruct",
        output_dir: str = "models/vish-ai-mini"
    ):
        self.base_model_name = base_model
        self.output_dir = output_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        os.makedirs(output_dir, exist_ok=True)
    
    def prepare_dataset(
        self,
        training_data: List[Dict[str, str]],
        tokenizer
    ) -> Dataset:
        """Convert training data to Hugging Face Dataset"""
        
        logger.info(f"Preparing {len(training_data)} samples for training...")
        
        # Format as instruction-response pairs
        formatted_data = []
        for item in training_data:
            # Create instruction format
            messages = [
                {"role": "user", "content": item["prompt"]},
                {"role": "assistant", "content": item["response"]}
            ]
            
            # Apply chat template
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False
            )
            
            formatted_data.append({"text": text})
        
        dataset = Dataset.from_list(formatted_data)
        logger.info(f"✅ Dataset prepared: {len(dataset)} samples")
        return dataset
    
    def tokenize_dataset(self, dataset: Dataset, tokenizer) -> Dataset:
        """Tokenize the dataset"""
        
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=512,  # Limit for free-tier efficiency
                return_tensors="pt"
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        return tokenized_dataset
    
    def fine_tune(
        self,
        min_samples: int = 10,
        epochs: int = 3,
        learning_rate: float = 2e-4,
        batch_size: int = 2,  # Small for free-tier
        use_quantization: bool = False
    ) -> Dict[str, any]:
        """
        Run LoRA fine-tuning on collected dataset
        
        Returns:
            Dict with training metrics and status
        """
        
        try:
            logger.info("=" * 60)
            logger.info("🚀 Starting VISH AI Self-Training Pipeline")
            logger.info("=" * 60)
            
            # Get dataset manager
            dataset_mgr = get_dataset_manager()
            
            # Prepare training data
            training_data = dataset_mgr.prepare_training_data(
                min_feedback_score=3.0,
                max_samples=1000  # Limit for efficiency
            )
            
            if len(training_data) < min_samples:
                logger.warning(f"Insufficient data: {len(training_data)} < {min_samples}")
                return {
                    "status": "skipped",
                    "reason": "insufficient_data",
                    "samples": len(training_data),
                    "required": min_samples
                }
            
            logger.info(f"📊 Training with {len(training_data)} samples")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                self.base_model_name,
                trust_remote_code=True
            )
            tokenizer.pad_token = tokenizer.eos_token
            
            # Load base model
            logger.info("📥 Loading base model...")
            model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                device_map=self.device,
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Configure LoRA
            lora_config = LoraConfig(
                r=16,  # Low rank for efficiency
                lora_alpha=32,
                target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
                lora_dropout=0.05,
                bias="none",
                task_type="CAUSAL_LM"
            )
            
            logger.info("🔧 Applying LoRA adapters...")
            model = get_peft_model(model, lora_config)
            model.print_trainable_parameters()
            
            # Prepare dataset
            dataset = self.prepare_dataset(training_data, tokenizer)
            tokenized_dataset = self.tokenize_dataset(dataset, tokenizer)
            
            # Training arguments (free-tier optimized)
            training_args = TrainingArguments(
                output_dir=f"{self.output_dir}/checkpoints",
                num_train_epochs=epochs,
                per_device_train_batch_size=batch_size,
                gradient_accumulation_steps=4,
                learning_rate=learning_rate,
                logging_steps=10,
                save_steps=100,
                save_total_limit=2,
                fp16=self.device == "cuda",
                optim="adamw_torch",
                warmup_steps=10,
                report_to="none",  # Disable wandb/tensorboard for simplicity
                remove_unused_columns=False
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False
            )
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=tokenized_dataset,
                data_collator=data_collator
            )
            
            # Train!
            logger.info("🎓 Starting training...")
            train_result = trainer.train()
            
            # Save the fine-tuned adapter
            final_path = f"{self.output_dir}/latest"
            model.save_pretrained(final_path)
            tokenizer.save_pretrained(final_path)
            
            logger.info(f"✅ Model saved to {final_path}")
            
            # Update metadata
            version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            metrics = {
                "train_loss": float(train_result.training_loss),
                "samples": len(training_data),
                "epochs": epochs,
                "device": self.device
            }
            
            model_handler = get_model_handler()
            model_handler.update_model_version(version, metrics)
            
            # Reload model in the handler
            reload_model()
            
            logger.info("=" * 60)
            logger.info("🎉 Training Complete!")
            logger.info(f"   Version: {version}")
            logger.info(f"   Loss: {metrics['train_loss']:.4f}")
            logger.info(f"   Samples: {metrics['samples']}")
            logger.info("=" * 60)
            
            return {
                "status": "success",
                "version": version,
                "metrics": metrics,
                "model_path": final_path
            }
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "status": "failed",
                "error": str(e)
            }


def run_training_pipeline(
    min_samples: int = 10,
    epochs: int = 3
) -> Dict[str, any]:
    """
    Main entry point for self-training pipeline
    Can be called from API or scheduled task
    """
    trainer = VishTrainer()
    result = trainer.fine_tune(
        min_samples=min_samples,
        epochs=epochs,
        batch_size=2,
        learning_rate=2e-4
    )
    return result
