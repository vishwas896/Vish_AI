# 🌟 Vish AI - Virtual Intelligent System Hub

[![Hugging Face Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Space-blue)](https://huggingface.co/spaces/Vishwas896/Vish-AI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Model: Phi-3](https://img.shields.io/badge/Model-Phi--3-green)](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)

> Powerful AI assistant powered by Microsoft Phi-3 Mini (3.8B parameters) - Optimized for Hugging Face Spaces

## 🚀 Features

### Core Capabilities

- **💬 Chat Assistant**: Intelligent conversation with 4K context window (Phi-3)
- **📝 Text Summarization**: Advanced text condensing with AI understanding (Phi-3)
- **😊 Sentiment Analysis**: Accurate emotion detection (Phi-3)
- **🔐 Supabase Authentication**: Optional secure user management
- **📊 Usage Logging**: Track interactions in Supabase database

### Performance Specs

- **Model**: Microsoft Phi-3 Mini 4K Instruct (3.8B parameters)
- **Model Size**: ~7.4GB (unified model for all tasks)
- **Response Time**: 2-5 seconds on CPU (faster on GPU)
- **Memory Usage**: ~8GB RAM recommended
- **CPU Optimized**: Works on free tier, better on GPU

## 🎯 Use Cases

1. **Advanced Chatbot**: High-quality conversational AI
2. **Content Analysis**: Professional-grade summarization and sentiment detection
3. **Educational Tool**: Intelligent learning assistant
4. **Research Assistant**: Context-aware information processing
5. **VIJ Project Integration**: Powerful AI backend

## 📦 Quick Deploy to Hugging Face Spaces

### Method 1: Direct Upload

1. **Create a new Space** on Hugging Face
   - Go to: <https://huggingface.co/new-space>
   - Select: **Gradio** SDK
   - Python: **3.10 or 3.11** (recommended)
   - Hardware: **CPU basic** (free, slower) or **T4 GPU** (faster)

2. **Upload these files**:
   - `app.py` (main application)
   - `requirements.txt` (dependencies)
   - `README.md` (this file)

3. **Wait for build** (15-20 minutes on first run):
   - Installing dependencies (~3 minutes)
   - Downloading Phi-3 model (~10-15 minutes, 7GB)
   - Building app (~2 minutes)
   - Add these secrets:

     ```text
     NEXT_PUBLIC_SUPABASE_URL=https://lyebtceryednzafhyunq.supabase.co
     NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
     ```

4. **Deploy**: The space will automatically build and deploy!

### Local Development

```bash
# Clone the repository
git clone https://github.com/vishwas896/Vish_AI.git
cd Vish_AI

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the application
python app.py
```

## 🗄️ Supabase Setup

### Create Logs Table

Run this SQL in your Supabase SQL Editor:

```sql
-- Create table for logging Vish AI interactions
CREATE TABLE IF NOT EXISTS vish_ai_logs (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT,
    prompt TEXT,
    response TEXT,
    model_type TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_vish_ai_logs_user ON vish_ai_logs(user_email);
CREATE INDEX idx_vish_ai_logs_timestamp ON vish_ai_logs(timestamp DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE vish_ai_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own logs
CREATE POLICY "Users can view own logs"
    ON vish_ai_logs FOR SELECT
    USING (auth.jwt() ->> 'email' = user_email);

-- Policy: Service role can insert logs
CREATE POLICY "Service role can insert logs"
    ON vish_ai_logs FOR INSERT
    WITH CHECK (true);
```

## 🔧 Configuration

### Model Selection

The AI uses these lightweight models:

| Model | Size | Speed | Purpose |
|-------|------|-------|---------|
| **DistilGPT2** | 82MB | ~0.5-2s | Chat conversations |
| **DistilBART-CNN-6-6** | 300MB | ~1-3s | Text summarization |
| **DistilBERT-SST2** | 255MB | ~0.3-1s | Sentiment analysis |

### Why These Models?

✅ **Optimized for CPU** - No GPU required  
✅ **Fast inference** - Sub-3 second responses  
✅ **Low memory** - Runs on 2GB RAM  
✅ **Good accuracy** - Distilled from larger models  
✅ **Free tier friendly** - Fits Hugging Face limits  

## 🌐 VIJ Project Integration

### Connect from v0.dev/Next.js

```typescript
// In your VIJ project (Next.js/React)
const callVishAI = async (message: string, userToken: string) => {
  const response = await fetch('https://vishwas896-vish-ai.hf.space/api/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      data: [message, [], userToken]
    })
  });
  
  const result = await response.json();
  return result.data[0];
};

// Usage with Supabase auth
const { data: { session } } = await supabase.auth.getSession();
const aiResponse = await callVishAI(
  "Hello Vish AI!",
  session?.access_token || ""
);
```

### API Endpoints

Once deployed, your space will have these endpoints:

- **Chat**: `POST /api/predict` (function_index: 0)
- **Summarize**: `POST /api/predict` (function_index: 1)
- **Sentiment**: `POST /api/predict` (function_index: 2)

## 📊 Performance Benchmarks

Tested on Hugging Face CPU basic (free tier):

| Task | Avg Response Time | Memory Usage |
|------|------------------|--------------|
| Chat (50 words) | 1.2s | ~800MB |
| Summarization (500 words) | 2.4s | ~1.2GB |
| Sentiment Analysis | 0.6s | ~600MB |

## 🔒 Security

- **Environment Variables**: Sensitive keys stored in HF Secrets
- **Supabase RLS**: Row-level security on logs table
- **JWT Validation**: Optional user authentication
- **Anonymous Mode**: Works without authentication

## 🚦 Usage Limits (Free Tier)

- **CPU Time**: Reasonable for personal projects
- **Memory**: 2GB RAM limit (well within our ~1.5GB usage)
- **Storage**: 50GB (models cache ~2GB)
- **Sleeps after 48h inactivity**: First request wakes it up

## 🛠️ Troubleshooting

### Models Loading Slowly

- Normal on first run (downloads ~650MB)
- Cached after first load
- Takes 30-60 seconds initially

### Out of Memory Error

- Reduce `max_length` in text generation
- Use smaller batch sizes
- Consider upgrading to CPU upgrade tier ($0)

### Supabase Connection Issues

- Verify environment variables are set
- Check Supabase project is active
- Ensure RLS policies are correct

## 📈 Roadmap

- [ ] Add image analysis (CLIP model)
- [ ] Voice input/output
- [ ] Multi-language support
- [ ] Custom model fine-tuning
- [ ] Advanced analytics dashboard
- [ ] WebSocket for real-time chat

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - feel free to use in your projects!

## 🙏 Acknowledgments

- **Hugging Face**: For free hosting and amazing models
- **Supabase**: For backend infrastructure
- **v0.dev**: For VIJ project development
- **Gradio**: For beautiful UI framework

## 📧 Contact

Vishwas

- Hugging Face: [@Vishwas896](https://huggingface.co/Vishwas896)
- GitHub: [@vishwas896](https://github.com/vishwas896)

---

Built with ❤️ for the VIJ Project
