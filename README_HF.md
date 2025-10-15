---
title: Vish AI
emoji: 🌟
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.19.2
app_file: app.py
pinned: false
license: mit
---

## Vish AI - Virtual Intelligent System Hub

Production-ready, lightweight, multimodal AI assistant optimized for Hugging Face Spaces

## Features

- **💬 Chat Assistant**: Natural conversation using DistilGPT2 (82MB)
- **📝 Text Summarization**: Condense articles with DistilBART (300MB)
- **😊 Sentiment Analysis**: Emotion detection with DistilBERT (255MB)
- **🔐 Supabase Integration**: User authentication & logging
- **⚡ Fast Performance**: 0.5-3s response time on CPU

## Performance

- **Total Model Size**: ~650MB
- **Memory Usage**: <2GB RAM
- **CPU Optimized**: No GPU required
- **Free Tier Friendly**: Runs on HF basic tier

## Configuration

### Required Secrets (in Space Settings)

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

### Optional Secrets

```env
SUPABASE_JWT_SECRET=your_jwt_secret
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## Models Used

| Model | Size | Purpose | Speed |
|-------|------|---------|-------|
| DistilGPT2 | 82MB | Chat | ~0.5-2s |
| DistilBART-CNN-6-6 | 300MB | Summarization | ~1-3s |
| DistilBERT-SST2 | 255MB | Sentiment | ~0.3-1s |

## 🌐 Integration

### API Usage

```python
import requests

response = requests.post(
    "https://vishwas896-vish-ai.hf.space/api/predict",
    json={
        "data": ["Hello Vish AI!", [], ""],
        "fn_index": 0  # 0=chat, 1=summarize, 2=sentiment
    }
)
```

### Next.js/React Integration

```typescript
const callVishAI = async (message: string) => {
  const res = await fetch('YOUR_HF_SPACE_URL/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      data: [message, [], ""],
      fn_index: 0
    })
  });
  const result = await res.json();
  return result.data[0];
};
```

## 🗄️ Supabase Setup

Run this SQL in your Supabase project:

```sql
CREATE TABLE vish_ai_logs (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT,
    prompt TEXT,
    response TEXT,
    model_type TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_vish_ai_logs_user ON vish_ai_logs(user_email);
CREATE INDEX idx_vish_ai_logs_timestamp ON vish_ai_logs(timestamp DESC);
```

## 🛠️ Local Development

```bash
# Clone repository
git clone https://huggingface.co/spaces/Vishwas896/Vish-AI
cd Vish-AI

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export NEXT_PUBLIC_SUPABASE_URL="your_url"
export NEXT_PUBLIC_SUPABASE_ANON_KEY="your_key"

# Run application
python app.py
```

## 📈 Usage Stats

- **Model Loading Time**: 30-60s (first run only)
- **Response Time**: 0.5-3s per request
- **Concurrent Users**: Up to 10-20 on free tier
- **Storage**: ~2GB (models cached)

## 🔒 Security

- Environment variables for sensitive keys
- Row-level security on Supabase
- Optional JWT authentication
- Anonymous mode supported

## 📝 License

MIT License - Free for personal and commercial use

## 🙏 Credits

- **Hugging Face**: Model hosting
- **Supabase**: Backend infrastructure
- **Gradio**: UI framework

---

**Built for the VIJ Project** | [GitHub](https://github.com/vishwas896/Vish_AI) | [Supabase](https://supabase.com)
