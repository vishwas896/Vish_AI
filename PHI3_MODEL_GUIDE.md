# Phi-3 Mini Unified Model Guide

## Overview

This project has been upgraded from using three separate lightweight models to a single unified **Microsoft Phi-3 Mini 4K Instruct** model that handles all AI tasks:

### Previous Architecture (Multi-Model)
- **DistilGPT2** (~82MB) - Chat
- **DistilBART-CNN** (~300MB) - Summarization  
- **DistilBERT-SST2** (~255MB) - Sentiment Analysis
- **Total**: ~650MB, 3 models to maintain

### New Architecture (Unified Model)
- **Phi-3 Mini 4K Instruct** (~7.4GB with optimizations)
- **Single model** for all tasks
- **Better quality** (3.8B parameters)
- **Fine-tunable** for custom requirements

---

## Model Capabilities

### 1. Chat Assistant
- Natural conversation with context awareness
- Maintains conversation history
- Provides helpful and concise responses
- Response time: ~1-3s on CPU

### 2. Text Summarization
- Summarizes long articles/documents
- Extracts key information
- Concise 2-3 sentence summaries
- Processing time: ~2-4s

### 3. Sentiment Analysis
- Detects positive, negative, or neutral sentiment
- Context-aware understanding
- Analysis time: ~0.5-2s

---

## Advantages of Phi-3

1. **Higher Quality**: 3.8B parameters vs 82M-300M in previous models
2. **Unified Architecture**: Single model is easier to maintain, fine-tune, and deploy
3. **Better Context Understanding**: 4K token context window
4. **Fine-tunable**: Can be customized for specific use cases
5. **Production Ready**: Microsoft-supported, actively maintained

---

## Fine-Tuning Phi-3 for Your Project

### Prerequisites
```bash
pip install transformers datasets peft bitsandbytes trl
```

### Step 1: Prepare Your Training Data

Create a JSONL file with your training examples:

```json
{"text": "User: What is Vish AI?\nAssistant: Vish AI is a Virtual Intelligent System Hub that provides chat, summarization, and sentiment analysis capabilities."}
{"text": "User: How does summarization work?\nAssistant: I analyze the text, identify key points, and condense them into a brief summary."}
```

### Step 2: Fine-Tuning Script

Create `fine_tune_phi3.py`:

```python
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch

# Load model and tokenizer
model_name = "microsoft/Phi-3-mini-4k-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

# Prepare model for training with LoRA (efficient fine-tuning)
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)

# Load your dataset
dataset = load_dataset("json", data_files="training_data.jsonl")

# Tokenize data
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="./phi3-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    warmup_steps=100,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_strategy="epoch",
    report_to="none"
)

# Create trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    tokenizer=tokenizer
)

# Start training
trainer.train()

# Save fine-tuned model
trainer.save_model("./phi3-vish-ai-finetuned")
tokenizer.save_pretrained("./phi3-vish-ai-finetuned")
```

### Step 3: Run Fine-Tuning

```bash
python fine_tune_phi3.py
```

### Step 4: Use Fine-Tuned Model

Update `app.py` to load your fine-tuned model:

```python
def initialize_models():
    global phi3_model, phi3_tokenizer
    
    # Load your fine-tuned model instead of base model
    model_path = "./phi3-vish-ai-finetuned"  # or upload to HuggingFace Hub
    
    phi3_tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True
    )
    
    phi3_model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="cpu",
        torch_dtype=torch.float32,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )
    
    return True
```

---

## Training Data Examples for Vish AI

### Chat Examples
```json
{"text": "User: What can you do?\nAssistant: I can help you with conversations, summarize long texts, and analyze sentiment in messages."}
{"text": "User: How are you?\nAssistant: I'm functioning well and ready to assist you! What would you like help with today?"}
{"text": "User: Explain quantum computing.\nAssistant: Quantum computing uses quantum mechanics principles to process information using qubits instead of traditional bits, allowing for exponentially faster computation for certain problems."}
```

### Summarization Examples
```json
{"text": "Summarize the following text concisely in 2-3 sentences:\n\nQuantum computing is a revolutionary technology that leverages quantum mechanics to solve complex problems faster than classical computers. Unlike traditional bits that are either 0 or 1, quantum bits (qubits) can exist in multiple states simultaneously through superposition. This allows quantum computers to process vast amounts of data and perform calculations that would take classical computers thousands of years to complete.\n\nSummary: Quantum computing uses quantum mechanics and qubits to solve complex problems exponentially faster than classical computers. Qubits can exist in multiple states simultaneously, enabling massive parallel processing capabilities."}
```

### Sentiment Examples
```json
{"text": "Analyze the sentiment of the following text. Respond with only one word: POSITIVE, NEGATIVE, or NEUTRAL.\n\nText: I absolutely love this product! It exceeded all my expectations.\n\nSentiment: POSITIVE"}
{"text": "Analyze the sentiment of the following text. Respond with only one word: POSITIVE, NEGATIVE, or NEUTRAL.\n\nText: This is the worst experience I've ever had. Completely disappointed.\n\nSentiment: NEGATIVE"}
{"text": "Analyze the sentiment of the following text. Respond with only one word: POSITIVE, NEGATIVE, or NEUTRAL.\n\nText: The weather today is cloudy with a chance of rain.\n\nSentiment: NEUTRAL"}
```

---

## Performance Optimization Tips

### 1. Use Quantization for Smaller Memory Footprint
```python
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3-mini-4k-instruct",
    quantization_config=quantization_config,
    device_map="auto",
    trust_remote_code=True
)
```

### 2. Batch Processing for Multiple Requests
```python
def batch_generate(prompts: list, max_new_tokens: int = 256):
    inputs = phi3_tokenizer(prompts, return_tensors="pt", padding=True)
    outputs = phi3_model.generate(**inputs, max_new_tokens=max_new_tokens)
    return [phi3_tokenizer.decode(out, skip_special_tokens=True) for out in outputs]
```

### 3. Caching for Repeated Queries
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_generate(prompt: str, max_new_tokens: int = 256):
    return generate_phi3_response(prompt, max_new_tokens)
```

---

## Deployment Options

### Hugging Face Spaces (Recommended)
- Upload fine-tuned model to HuggingFace Hub
- Update `app.py` to reference your model
- Deploy with 2-4 CPU cores for optimal performance

### Local Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "app.py"]
```

---

## Model Comparison

| Feature | Previous (3 Models) | New (Phi-3 Unified) |
|---------|---------------------|---------------------|
| **Total Size** | ~650MB | ~7.4GB (optimized) |
| **Parameters** | 82M-300M each | 3.8B |
| **Quality** | Good for basic tasks | Excellent, context-aware |
| **Maintenance** | 3 models to update | 1 model to maintain |
| **Fine-tuning** | Complex (3 separate) | Simple (1 model) |
| **Response Quality** | Decent | Superior |
| **Context Window** | Limited | 4K tokens |
| **Speed** | Faster | Good (1-4s) |

---

## FAQ

### Q: Is Phi-3 free to use?
**A:** Yes, Phi-3 Mini is open-source and available under MIT license.

### Q: Can I use this on Hugging Face free tier?
**A:** Yes, but you may need persistent storage or use model quantization for optimal performance.

### Q: How long does fine-tuning take?
**A:** Depends on dataset size. For ~1000 examples with LoRA, approximately 1-2 hours on a single GPU.

### Q: Can I use GPU acceleration?
**A:** Yes! Change `device_map="cpu"` to `device_map="auto"` to use GPU if available.

### Q: What if I want smaller memory footprint?
**A:** Use 4-bit or 8-bit quantization (see optimization tips above).

---

## Support & Resources

- **Phi-3 Documentation**: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct
- **Fine-tuning Guide**: https://huggingface.co/docs/transformers/training
- **LoRA/PEFT**: https://huggingface.co/docs/peft
- **Project Issues**: Create an issue in your repository

---

## License

This project uses the Microsoft Phi-3 Mini model under the MIT License.
