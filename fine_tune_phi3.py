"""
Fine-tune Phi-3 Mini for Vish AI Project
This script demonstrates how to fine-tune the Phi-3 model on custom data
"""

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import os

# Configuration
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
OUTPUT_DIR = "./phi3-vish-ai-finetuned"
TRAINING_DATA = "training_data.jsonl"  # Create this file with your training examples

# Check if CUDA is available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🖥️  Using device: {device}")

def main():
    print("=" * 60)
    print("🚀 Starting Phi-3 Fine-Tuning for Vish AI")
    print("=" * 60)
    
    # Step 1: Load tokenizer and model
    print("\n📥 Loading tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    
    # Set padding token if not set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None,
        trust_remote_code=True
    )
    
    if device == "cpu":
        model = model.to(device)
    
    print("✅ Model and tokenizer loaded")
    
    # Step 2: Configure LoRA for efficient fine-tuning
    print("\n⚙️  Configuring LoRA (Parameter-Efficient Fine-Tuning)...")
    lora_config = LoraConfig(
        r=16,  # Rank of the low-rank matrices
        lora_alpha=32,  # Scaling factor
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # Which modules to apply LoRA to
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    if device == "cuda":
        model = prepare_model_for_kbit_training(model)
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Step 3: Load and prepare training data
    print("\n📚 Loading training data...")
    
    if not os.path.exists(TRAINING_DATA):
        print(f"⚠️  Training data file '{TRAINING_DATA}' not found!")
        print("\nCreating sample training data...")
        create_sample_training_data()
    
    dataset = load_dataset("json", data_files=TRAINING_DATA)
    
    # Tokenize dataset
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
    
    print("🔄 Tokenizing dataset...")
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset["train"].column_names
    )
    
    print(f"✅ Dataset loaded: {len(tokenized_dataset['train'])} examples")
    
    # Step 4: Configure training arguments
    print("\n⚙️  Configuring training parameters...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=2 if device == "cuda" else 1,
        gradient_accumulation_steps=8,
        warmup_steps=100,
        learning_rate=2e-4,
        fp16=device == "cuda",
        logging_steps=10,
        save_strategy="epoch",
        save_total_limit=2,
        report_to="none",
        remove_unused_columns=True,
        push_to_hub=False
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Step 5: Create Trainer
    print("\n🎓 Creating trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        tokenizer=tokenizer,
        data_collator=data_collator
    )
    
    # Step 6: Start training
    print("\n🚀 Starting training...")
    print("=" * 60)
    trainer.train()
    
    # Step 7: Save fine-tuned model
    print("\n💾 Saving fine-tuned model...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print("=" * 60)
    print("✅ Fine-tuning complete!")
    print(f"📁 Model saved to: {OUTPUT_DIR}")
    print("\nTo use your fine-tuned model:")
    print(f"1. Update app.py to load from '{OUTPUT_DIR}'")
    print("2. Or upload to HuggingFace Hub and use that path")
    print("=" * 60)


def create_sample_training_data():
    """Create sample training data if file doesn't exist"""
    
    sample_data = [
        # Chat examples
        {"text": "User: What is Vish AI?\nAssistant: Vish AI is a Virtual Intelligent System Hub that provides chat, summarization, and sentiment analysis capabilities using advanced AI."},
        {"text": "User: How does the chat feature work?\nAssistant: The chat feature uses the Phi-3 model to generate natural, context-aware responses based on your questions and conversation history."},
        {"text": "User: What can you help me with?\nAssistant: I can help you with conversations, summarize long documents, and analyze the sentiment of text. Just ask me anything!"},
        
        # Summarization examples
        {"text": "Summarize the following text concisely in 2-3 sentences:\n\nArtificial Intelligence has revolutionized many industries by automating tasks, improving decision-making, and creating new possibilities. Machine learning, a subset of AI, enables computers to learn from data without explicit programming. This technology is now used in healthcare for diagnosis, in finance for fraud detection, and in transportation for autonomous vehicles.\n\nSummary: Artificial Intelligence has transformed industries through automation and enhanced decision-making capabilities. Machine learning allows computers to learn from data autonomously, with applications spanning healthcare diagnostics, financial fraud detection, and self-driving vehicles."},
        
        # Sentiment examples
        {"text": "Analyze the sentiment of the following text. Respond with only one word: POSITIVE, NEGATIVE, or NEUTRAL.\n\nText: I love using this AI assistant! It's incredibly helpful and fast.\n\nSentiment: POSITIVE"},
        {"text": "Analyze the sentiment of the following text. Respond with only one word: POSITIVE, NEGATIVE, or NEUTRAL.\n\nText: This service is disappointing and doesn't meet my expectations.\n\nSentiment: NEGATIVE"},
    ]
    
    import json
    with open(TRAINING_DATA, 'w') as f:
        for item in sample_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"✅ Created sample training data: {TRAINING_DATA}")
    print(f"   Add more examples to improve model performance!")


if __name__ == "__main__":
    main()
