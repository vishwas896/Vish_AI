# 🌟 VISH AI - Self-Training AI System

[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Model: Phi-3](https://img.shields.io/badge/Model-Phi--3-green)](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)

> **Production-ready AI assistant that learns from user interactions and improves itself automatically**

## 🚀 Features

### Core Capabilities
- **💬 Intelligent Chat Assistant** - Context-aware conversations
- **📝 Resume Builder** - Professional career guidance
- **🔬 Research Assistant** - Information gathering & analysis
- **💼 Business Consultant** - Strategic advice & insights

### Self-Training System
- **📊 Automatic Data Collection** - Every interaction is saved
- **⭐ User Feedback System** - Rate responses 1-5 stars
- **🎓 LoRA Fine-Tuning** - Continuous model improvement
- **📈 Performance Tracking** - Monitor improvements over time

### Technical Stack
- **Model**: Microsoft Phi-3 Mini 4K Instruct (3.8B params)
- **Training**: LoRA (PEFT) for efficient fine-tuning
- **Backend**: FastAPI with async support
- **Frontend**: Multi-tab Gradio interface
- **Storage**: Lightweight JSONL files
- **Deployment**: Docker + Hugging Face Spaces

---

## 📦 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/vishwas896/Vish_AI.git
cd Vish_AI

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.main
```

Visit: `http://localhost:7860`

### Docker Deployment

```bash
# Build Docker image
docker build -t vish-ai .

# Run container
docker run -p 7860:7860 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  vish-ai
```

### Hugging Face Spaces

1. **Create new Space**: https://huggingface.co/new-space
2. **Settings**:
   - SDK: **Gradio**
   - Python: **3.10 or 3.11**
   - Hardware: **CPU Basic** (free) or **T4 GPU** (faster)
3. **Upload files**:
   - `app/` directory (all Python files)
   - `requirements.txt`
   - `Dockerfile`
   - `README.md`
4. **Set environment variable** (optional):
   ```
   VISH_ADMIN_KEY=your-secret-key
   ```

---

## 🏗️ Project Structure

```
vish-ai/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI + Gradio server
│   ├── model_handler.py        # Phi-3 model management
│   ├── dataset_manager.py      # Data collection & storage
│   ├── retrain.py              # LoRA fine-tuning pipeline
│   ├── gradio_ui.py            # Multi-tab Gradio interface
│   └── routes/
│       ├── __init__.py
│       ├── chat.py             # Chat API endpoint
│       ├── feedback.py         # Feedback collection
│       └── retrain.py          # Admin training endpoint
│
├── data/
│   ├── vish_dataset.jsonl      # User interactions
│   ├── feedback.jsonl          # User ratings
│   └── research_data.jsonl     # Research data
│
├── models/
│   └── vish-ai-mini/
│       ├── latest/             # Fine-tuned LoRA adapters
│       └── metadata.json       # Version & metrics
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 💡 How It Works

### 1. Data Collection
Every chat interaction is automatically saved with:
- User prompt
- AI response
- Category (assistant, resume, research, business)
- Timestamp
- Metadata (response time, model version)

```json
{
  "id": "a1b2c3d4",
  "user_prompt": "How do I write a resume?",
  "ai_response": "Here's how to create a professional resume...",
  "category": "resume",
  "timestamp": "2024-10-16T14:30:00Z",
  "feedback_score": null
}
```

### 2. User Feedback
Users rate responses 1-5 stars:
- ⭐⭐⭐⭐⭐ Excellent (5)
- ⭐⭐⭐⭐ Good (4)
- ⭐⭐⭐ Acceptable (3)
- ⭐⭐ Poor (2)
- ⭐ Very Poor (1)

Only interactions with rating ≥ 3 are used for training.

### 3. Self-Training
When triggered (manually or scheduled):
1. **Filter** → Select high-quality interactions (score ≥ 3)
2. **Clean** → Deduplicate and validate data
3. **Train** → Fine-tune Phi-3 with LoRA adapters
4. **Save** → Create new model version
5. **Deploy** → Automatically reload the improved model

### 4. Continuous Improvement
Each training cycle:
- Creates a versioned model (e.g., `v20241016_143022`)
- Tracks performance metrics (loss, samples, epochs)
- Updates metadata automatically
- Model gets better at your specific use cases

---

## 🔧 API Endpoints

### Chat
```bash
POST /api/chat
{
  "message": "Help me write a resume",
  "category": "resume",
  "user_id": "user123"
}
```

### Feedback
```bash
POST /api/feedback
{
  "interaction_id": "a1b2c3d4",
  "score": 5,
  "comment": "Excellent advice!"
}
```

### Statistics
```bash
GET /api/stats
```

### Admin - Retrain
```bash
POST /api/admin/retrain
{
  "min_samples": 10,
  "epochs": 3,
  "admin_key": "your-secret-key"
}
```

### Health Check
```bash
GET /health
```

---

## 🎯 Usage Examples

### Example 1: General Chat
```
User: What is artificial intelligence?
VISH: Artificial intelligence (AI) is a branch of computer science...
⚡ Response time: 2.3s | ID: a1b2c3d4
```

### Example 2: Resume Builder
```
Category: Resume
User: Help me write a software engineer resume
VISH: Here's a professional software engineer resume structure...
[Detailed resume guidance]
```

### Example 3: Research
```
Category: Research
User: What are the latest trends in AI?
VISH: Current AI trends include:
1. Large Language Models (LLMs)...
```

---

## 📊 Dataset Statistics

View real-time stats in the Gradio interface:

- **Total Interactions**: 1,234
- **Total Feedback**: 456 ratings
- **Average Rating**: 4.2/5.0 ⭐
- **By Category**:
  - Assistant: 500
  - Resume: 300
  - Research: 250
  - Business: 184

---

## 🔐 Security & Privacy

### Admin Access
Set admin key for training control:
```bash
export VISH_ADMIN_KEY="your-secret-key-here"
```

### Data Privacy
- All data stored **locally** in `/data` directory
- No external data transmission
- User IDs are optional
- Feedback is anonymous

### Production Deployment
For production use:
1. Use proper authentication (JWT, OAuth)
2. Set strong admin keys
3. Enable HTTPS
4. Regular backups of `/data` and `/models`
5. Monitor disk space (models can be large)

---

## ⚡ Performance Optimization

### Free-Tier Friendly
- **CPU Optimized**: Works on Hugging Face CPU Basic
- **Quantization**: Optional 4-bit for memory efficiency
- **Batch Size**: Small (2) for limited RAM
- **Model Size**: ~7.4GB base + LoRA adapters (~100MB)

### GPU Acceleration
For faster performance:
- Upgrade to T4 GPU ($0.60/hr)
- 5-10x faster inference
- Better for high traffic

### Memory Usage
- **CPU Basic**: ~8GB RAM required
- **With Quantization**: ~4-6GB RAM
- **LoRA Adapters**: Minimal overhead (~100MB)

---

## 🎓 Training Process

### Automatic Triggers
Train when:
- 10+ new high-quality interactions
- Weekly scheduled task
- Manual admin trigger

### Training Configuration
```python
{
  "min_samples": 10,        # Minimum interactions
  "epochs": 3,              # Training epochs
  "batch_size": 2,          # For free-tier
  "learning_rate": 2e-4,    # LoRA learning rate
  "lora_r": 16,             # LoRA rank
  "lora_alpha": 32          # LoRA alpha
}
```

### Expected Results
- **Training Time**: 10-30 minutes (CPU), 2-5 minutes (GPU)
- **Model Size**: Base (7.4GB) + Adapter (~100MB)
- **Improvement**: Measurable after 50+ quality interactions

---

## 🐛 Troubleshooting

### Model Not Loading
```bash
# Check logs
tail -f logs/vish_ai.log

# Verify dependencies
pip list | grep transformers
```

### Out of Memory
```python
# Use quantization in model_handler.py
load_model(use_quantization=True)
```

### Training Fails
- Check minimum samples (need ≥10)
- Verify disk space (need ~10GB free)
- Check GPU availability
- Review error logs

---

## 🤝 Contributing

Contributions welcome! Areas to improve:

1. **Web Research Integration** - Add DuckDuckGo/Wikipedia APIs
2. **Voice Input/Output** - Speech-to-text & text-to-speech
3. **Vector Database** - Add FAISS for semantic search
4. **Document Processing** - PDF/DOCX parsing
5. **Multi-language Support** - Expand beyond English

---

## 📝 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- **Microsoft** - Phi-3 Mini model
- **Hugging Face** - Transformers, PEFT, Datasets
- **Gradio** - Interactive UI framework
- **FastAPI** - Modern Python web framework

---

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: your-email@example.com

---

## 🎉 What You Get

✨ **Production-ready AI assistant** with:
- Multi-category support (chat, resume, research, business)
- Automatic data collection
- User feedback system
- Self-training with LoRA
- Performance tracking
- REST API + Gradio UI
- Docker deployment
- Free-tier compatible

**Total Setup**: Just upload to Hugging Face Spaces and it works! 🚀

---

Built with ❤️ by Vishwas | VIJ Project | Powered by Microsoft Phi-3
