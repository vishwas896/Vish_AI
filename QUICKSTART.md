# 🚀 VISH AI - Quick Start Guide

## Installation & Setup (5 minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- Gradio (UI)
- FastAPI (API)
- Transformers (Phi-3)
- PEFT (LoRA training)
- Datasets (data handling)

### Step 2: Start the Server

```bash
python start.py
```

**Or manually:**
```bash
python -m app.main
```

### Step 3: Open Browser

Visit: **http://localhost:7860**

---

## 🎯 First Steps

### 1. Try the Chat
- Go to "💬 VISH Assistant" tab
- Type: "Tell me about artificial intelligence"
- Click Send
- Notice the interaction ID in the response

### 2. Submit Feedback
- Copy the interaction ID (e.g., `a1b2c3d4`)
- Go to "⭐ Feedback" tab
- Paste the ID
- Rate 1-5 stars
- Click "Submit Feedback"

### 3. Check Statistics
- Go to "📊 Statistics" tab
- Click "🔄 Refresh Stats"
- See your interactions and ratings

### 4. Train the Model (After 10+ interactions)
- Go to "🎓 Training (Admin)" tab
- Set minimum samples: 10
- Set epochs: 3
- Enter admin key: `vish-admin-2024` (default)
- Click "🚀 Start Training"
- Wait 10-30 minutes for training

---

## 📝 Category Examples

### General Assistant
```
Category: assistant
Question: "What is machine learning?"
```

### Resume Builder
```
Category: resume
Question: "Help me write a software engineer resume"
```

### Research
```
Category: research
Question: "Explain quantum computing"
```

### Business
```
Category: business
Question: "How do I create a business plan?"
```

---

## 🔐 Admin Key

Default admin key: `vish-admin-2024`

**Change it:**
```bash
export VISH_ADMIN_KEY="your-secret-key"
```

Or in `.env` file:
```
VISH_ADMIN_KEY=your-secret-key
```

---

## 📊 Understanding the System

### Data Flow
1. **User chats** → Saved to `data/vish_dataset.jsonl`
2. **User rates** → Saved to `data/feedback.jsonl`
3. **Training runs** → Creates `models/vish-ai-mini/latest/`
4. **Model reloads** → Uses improved version automatically

### File Structure
```
data/
  ├── vish_dataset.jsonl     # All interactions
  ├── feedback.jsonl         # User ratings
  └── research_data.jsonl    # Research data

models/
  └── vish-ai-mini/
      ├── latest/            # LoRA adapters
      └── metadata.json      # Version info
```

---

## 🎓 Training Process

### When to Train
- After collecting 10+ interactions
- After significant feedback
- Weekly/monthly for continuous improvement

### Training Time
- **CPU**: 10-30 minutes
- **GPU**: 2-5 minutes

### What Gets Trained
- High-quality interactions (rating ≥ 3)
- Deduplicated data
- LoRA adapters only (efficient!)

### Model Versions
Each training creates a version:
- `v20241016_143022`
- `v20241017_095234`
- Latest version is used automatically

---

## 🚀 Deployment

### Hugging Face Spaces

1. Create Space: https://huggingface.co/new-space
2. Upload files:
   - `app/` folder
   - `requirements.txt`
   - `Dockerfile`
   - `README.md`
3. Set hardware: CPU Basic (free) or T4 GPU
4. Wait for build (~15-20 minutes first time)
5. Done! Your AI is live

### Docker

```bash
# Build
docker build -t vish-ai .

# Run
docker run -p 7860:7860 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  -e VISH_ADMIN_KEY=your-key \
  vish-ai
```

---

## ⚡ Quick Tips

1. **Start with general questions** to build dataset
2. **Rate honestly** - only good data improves the model
3. **Train regularly** - weekly is good
4. **Check stats** - monitor improvement
5. **Backup data** - copy `/data` and `/models` regularly

---

## 🐛 Common Issues

### "Model not loaded"
- Wait for initial download (~7GB, 10-15 min)
- Check logs for errors
- Verify internet connection

### "Insufficient data for training"
- Need at least 10 interactions
- Check: `curl http://localhost:7860/api/stats`

### "Out of memory"
- Use quantization (edit `model_handler.py`)
- Reduce batch size in `retrain.py`
- Upgrade to GPU

---

## 📚 Next Steps

1. **Explore API**: Visit `http://localhost:7860/docs`
2. **Read Full README**: See `README_SELF_TRAINING.md`
3. **Customize**: Edit system prompts in `gradio_ui.py`
4. **Integrate**: Use API endpoints in your apps

---

## 🎉 Success!

You now have a self-improving AI assistant that:
- ✅ Learns from your conversations
- ✅ Improves with your feedback
- ✅ Trains automatically with LoRA
- ✅ Tracks performance over time
- ✅ Works on free-tier hardware

**Happy chatting! 🤖**

---

Built with ❤️ by Vishwas | Questions? Open an issue!
