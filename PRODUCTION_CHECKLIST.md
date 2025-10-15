# Production Deployment Checklist

## Pre-Deployment Checklist

### 1. Files Ready

- [x] `app.py` - Production-ready with fallback modes
- [x] `requirements.txt` - Python 3.10/3.11 compatible
- [x] `.python-version` - Specifies Python 3.11
- [x] `README_HF.md` - Hugging Face Space documentation
- [x] `.env` - Local environment (DO NOT COMMIT)
- [x] `supabase_setup.sql` - Database schema

### 2. Environment Variables Required

#### Minimum (for basic functionality)

```bash
NEXT_PUBLIC_SUPABASE_URL=https://lyebtceryednzafhyunq.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Optional (for advanced features)

```bash
SUPABASE_JWT_SECRET=CDELVoOBAyFycUNWHHSwZIRsiZHS8OcQlzFh0AJYOd6...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Deployment Steps for Hugging Face Spaces

### Step 1: Create Hugging Face Space

1. Go to <https://huggingface.co/new-space>
2. Fill in details:
   - **Owner**: Vishwas896
   - **Space name**: Vish-AI
   - **SDK**: Gradio
   - **Hardware**: CPU basic (FREE)
   - **Visibility**: Public
3. Click "Create Space"

### Step 2: Push Code to Hugging Face

```bash
# Option A: Using Git CLI
cd /workspaces/Vish_AI

# Initialize git (if not already)
git init
git add app.py requirements.txt .python-version README_HF.md
git commit -m "Production-ready Vish AI"

# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/Vishwas896/Vish-AI
git push hf main

# Option B: Using HF Hub CLI
pip install huggingface_hub
huggingface-cli login
huggingface-cli upload Vishwas896/Vish-AI ./app.py app.py
huggingface-cli upload Vishwas896/Vish-AI ./requirements.txt requirements.txt
huggingface-cli upload Vishwas896/Vish-AI ./.python-version .python-version

# Option C: Using Web Interface
# Just drag and drop files to https://huggingface.co/spaces/Vishwas896/Vish-AI/tree/main
```

### Step 3: Configure Secrets

1. Go to: <https://huggingface.co/spaces/Vishwas896/Vish-AI/settings>
2. Scroll to "Repository secrets"
3. Add secrets one by one:

```text
Name: NEXT_PUBLIC_SUPABASE_URL
Value: https://lyebtceryednzafhyunq.supabase.co

Name: NEXT_PUBLIC_SUPABASE_ANON_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5ZWJ0Y2VyeWVkbnphZmh5dW5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcyNjQ3ODksImV4cCI6MjA3Mjg0MDc4OX0.uP_MWQ4SAzGpSvYWIdAlq6qz86_DsTSoSmqBsBl0O10
```

### Step 4: Setup Supabase Database

1. Go to: <https://supabase.com/dashboard/project/lyebtceryednzafhyunq/sql>
2. Copy and paste the entire contents of `supabase_setup.sql`
3. Click "Run"
4. Verify table created: `vish_ai_logs`

### Step 5: Wait for Build

1. Monitor build at: <https://huggingface.co/spaces/Vishwas896/Vish-AI/logs>
2. Build time: ~3-5 minutes
3. Model download: ~2-3 minutes (first run only)
4. Total startup time: ~5-8 minutes

### Step 6: Test the Deployment

1. Visit: <https://huggingface.co/spaces/Vishwas896/Vish-AI>
2. Test features:
   - ✅ Chat interface
   - ✅ Text summarization
   - ✅ Sentiment analysis
3. Check logs in Supabase

## Production Features

### What's Included

1. **Graceful Degradation**
   - Works without PyTorch (demo mode)
   - Works without Supabase (no logging)
   - Clear user feedback

2. **Error Handling**
   - Try-catch blocks on all operations
   - User-friendly error messages
   - Fallback responses

3. **Performance Optimization**
   - Lazy model loading
   - CPU-optimized inference
   - Response time tracking

4. **Security**
   - Environment variable protection
   - Optional JWT authentication
   - Supabase RLS policies

5. **Monitoring**
   - Usage logging to database
   - User tracking
   - Performance metrics

## Configuration Options

### Model Configuration (in app.py)

```python
# Chat model
model="distilgpt2"  # 82MB, fast
max_length=150      # Response length

# Summarization
model="sshleifer/distilbart-cnn-6-6"  # 300MB
max_length=130      # Summary length
min_length=30       # Minimum summary

# Sentiment
model="distilbert-base-uncased-finetuned-sst-2-english"  # 255MB
```

### Gradio Configuration

```python
server_name="0.0.0.0"  # Listen on all interfaces
server_port=7860        # Default Gradio port
share=False             # Don't create public link
queue=True              # Enable request queuing
```

## Expected Performance

### On Hugging Face Free Tier (CPU Basic)

| Metric | Value |
|--------|-------|
| Cold Start | 5-8 minutes (first time) |
| Warm Start | 10-30 seconds |
| Chat Response | 0.5-2 seconds |
| Summarization | 1-3 seconds |
| Sentiment | 0.3-1 second |
| Memory Usage | 1.5-2GB |
| Concurrent Users | 10-20 |

### Model Sizes

| Model | Download Size | Memory Usage |
|-------|---------------|--------------|
| DistilGPT2 | 82 MB | ~300 MB |
| DistilBART | 300 MB | ~800 MB |
| DistilBERT | 255 MB | ~500 MB |
| **Total** | **~650 MB** | **~1.6 GB** |

## Troubleshooting

### Issue: Space won't start

**Solution:**

- Check build logs for errors
- Verify `requirements.txt` syntax
- Ensure `.python-version` is 3.11

### Issue: Models not loading

**Solution:**

- Wait 5-8 minutes on first start
- Check HF Space has enough memory
- Verify internet connection for model download

### Issue: Supabase connection failed

**Solution:**

- Verify secrets are set correctly
- Check Supabase project is active
- Test connection from SQL editor

### Issue: Import errors

**Solution:**

- Check Python version is 3.10 or 3.11
- Verify all dependencies in requirements.txt
- Clear cache and rebuild

## Update Workflow

### To update your deployed space

```bash
# Make changes locally
nano app.py

# Test locally
python app.py

# Commit and push
git add .
git commit -m "Update: description of changes"
git push hf main

# HF will automatically rebuild
```

## Scaling Options

### Free Tier → Paid Tier

If you need more power:

1. **CPU Upgrade** ($0-5/month)
   - More concurrent users
   - Faster response times

2. **GPU T4** ($0.60/hour)
   - 10x faster inference
   - Larger models possible

3. **Persistent Storage**
   - Model caching
   - Faster restarts

## Success Criteria

### Deployment is successful when

1. Space status shows "Running"
2. All 3 tabs work (Chat, Summarize, Sentiment)
3. Models load within 8 minutes
4. Responses are generated successfully
5. Supabase logging works (check database)
6. No errors in HF logs

## Support

### If you encounter issues

1. **Check Documentation**
   - README.md
   - DEPLOYMENT.md
   - This checklist

2. **Review Logs**
   - HF Space logs
   - Browser console
   - Supabase logs

3. **Common Resources**
   - [HF Spaces Docs](https://huggingface.co/docs/hub/spaces)
   - [Gradio Docs](https://gradio.app/docs)
   - [Supabase Docs](https://supabase.com/docs)

---

## Post-Deployment

### After successful deployment

1. ✅ Test all features
2. ✅ Share the link: `https://huggingface.co/spaces/Vishwas896/Vish-AI`
3. ✅ Integrate with VIJ project
4. ✅ Monitor usage in Supabase
5. ✅ Star the repository!

---

Ready to deploy? Let's go!
