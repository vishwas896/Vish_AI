# 🚀 Deploying Vish AI to Hugging Face Spaces

## Step-by-Step Deployment Guide

### 1️⃣ Prepare Your Files

You already have these files in your repository:

- ✅ `app.py` - Main application
- ✅ `requirements.txt` - Dependencies
- ✅ `.env` - Environment variables (don't push this!)
- ✅ `README.md` - Documentation

### 2️⃣ Create Hugging Face Space

1. **Go to Hugging Face**:
   - Visit: <https://huggingface.co/new-space>
   - Or directly: <https://huggingface.co/spaces/Vishwas896/Vish-AI/settings>

2. **Configure Space**:

   ```text
   Owner: Vishwas896
   Space name: Vish-AI
   License: MIT
   SDK: Gradio
   SDK version: 4.19.2
   Hardware: CPU basic (FREE)
   Visibility: Public
   ```

3. **Click "Create Space"**

### 3️⃣ Push Code to Hugging Face

#### Option A: Using Git (Recommended)

```bash
# Navigate to your project
cd /workspaces/Vish_AI

# Add Hugging Face as remote
git remote add hf https://huggingface.co/spaces/Vishwas896/Vish-AI

# If you need to authenticate, use your HF token
# Get token from: https://huggingface.co/settings/tokens
git remote set-url hf https://YOUR_HF_USERNAME:YOUR_HF_TOKEN@huggingface.co/spaces/Vishwas896/Vish-AI

# Stage your files
git add app.py requirements.txt README.md .gitignore

# Commit
git commit -m "Initial deployment of Vish AI"

# Push to Hugging Face
git push hf main
```

#### Option B: Using Web Interface

1. Go to: <https://huggingface.co/spaces/Vishwas896/Vish-AI/tree/main>
2. Click "Add file" → "Upload files"
3. Drag and drop:
   - `app.py`
   - `requirements.txt`
   - `README.md`
4. Click "Commit changes to main"

### 4️⃣ Configure Secrets

**IMPORTANT**: Never commit `.env` to public repository!

1. Go to: <https://huggingface.co/spaces/Vishwas896/Vish-AI/settings>

2. Scroll to **"Repository secrets"**

3. Add these secrets one by one:

```text
Name: NEXT_PUBLIC_SUPABASE_URL
Value: https://lyebtceryednzafhyunq.supabase.co

Name: NEXT_PUBLIC_SUPABASE_ANON_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5ZWJ0Y2VyeWVkbnphZmh5dW5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcyNjQ3ODksImV4cCI6MjA3Mjg0MDc4OX0.uP_MWQ4SAzGpSvYWIdAlq6qz86_DsTSoSmqBsBl0O10

Name: SUPABASE_JWT_SECRET
Value: CDELVoOBAyFycUNWHHSwZIRsiZHS8OcQlzFh0AJYOd6odwTFbtDNEmouSrUNX32RF37myYaOJjOdtiX0PW+55g==

Name: SUPABASE_SERVICE_ROLE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5ZWJ0Y2VyeWVkbnphZmh5dW5xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzI2NDc4OSwiZXhwIjoyMDcyODQwNzg5fQ.IKooD0ZctN1Y_ET6-xiEQQAjPjsRn9ePYPyLUop7O0A
```

### 5️⃣ Wait for Build

1. The space will automatically start building
2. You'll see logs at: <https://huggingface.co/spaces/Vishwas896/Vish-AI/logs>
3. Building takes ~3-5 minutes (downloading models)
4. Status will change from "Building" → "Running"

### 6️⃣ Test Your Space

1. Visit: <https://huggingface.co/spaces/Vishwas896/Vish-AI>
2. Wait for models to load (30-60 seconds on first run)
3. Try the chat interface
4. Test summarization and sentiment analysis

### 7️⃣ Set Up Supabase Database

Run this SQL in your Supabase SQL Editor (<https://supabase.com/dashboard/project/lyebtceryednzafhyunq/sql>):

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

-- Create indexes
CREATE INDEX idx_vish_ai_logs_user ON vish_ai_logs(user_email);
CREATE INDEX idx_vish_ai_logs_timestamp ON vish_ai_logs(timestamp DESC);

-- Enable RLS
ALTER TABLE vish_ai_logs ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view own logs"
    ON vish_ai_logs FOR SELECT
    USING (auth.jwt() ->> 'email' = user_email);

CREATE POLICY "Service role can insert logs"
    ON vish_ai_logs FOR INSERT
    WITH CHECK (true);
```

## 🔍 Verification Checklist

- [ ] Space is running at: <https://huggingface.co/spaces/Vishwas896/Vish-AI>
- [ ] All environment secrets are configured
- [ ] Models loaded successfully (check logs)
- [ ] Chat interface works
- [ ] Summarization works
- [ ] Sentiment analysis works
- [ ] Supabase logging table created
- [ ] No errors in logs

## 🎨 Customization

### Change Model Names

Edit `app.py` to use different models:

```python
# Replace DistilGPT2 with other lightweight models
text_generator = pipeline(
    "text-generation",
    model="gpt2",  # or "EleutherAI/gpt-neo-125M"
    device=-1
)
```

### Add Custom Branding

Update the Gradio theme in `app.py`:

```python
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="green"
    ),
    title="Vish AI",
    css=".gradio-container {background: linear-gradient(to right, #667eea, #764ba2);}"
) as demo:
```

### Enable Authentication

Uncomment authentication check in `app.py`:

```python
def chat_with_vish(message: str, history: list, auth_token: str = "") -> str:
    user_info = verify_user_token(auth_token)
    
    # Enforce authentication
    if not user_info.get("authenticated"):
        return "⚠️ Please provide a valid authentication token."
    
    # ... rest of the function
```

## 🐛 Troubleshooting

### Space Won't Start

**Check logs**: <https://huggingface.co/spaces/Vishwas896/Vish-AI/logs>

Common issues:

- Missing dependencies → Check `requirements.txt`
- Port conflicts → Gradio uses 7860 by default
- Memory issues → Reduce model batch sizes

### Models Not Loading

```python
# Add more detailed logging in app.py
def initialize_models():
    import logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        print("Starting model initialization...")
        # ... rest of code
```

### Supabase Connection Fails

1. Verify secrets are set correctly
2. Check Supabase project is active
3. Test connection manually:

```python
from supabase import create_client
client = create_client(SUPABASE_URL, SUPABASE_KEY)
print(client.table("vish_ai_logs").select("*").limit(1).execute())
```

## 📊 Monitoring

### Check Usage

1. **Hugging Face Analytics**:
   - <https://huggingface.co/spaces/Vishwas896/Vish-AI/analytics>

2. **Supabase Dashboard**:
   - <https://supabase.com/dashboard/project/lyebtceryednzafhyunq>

3. **View Logs**:

   ```sql
   SELECT * FROM vish_ai_logs 
   ORDER BY timestamp DESC 
   LIMIT 100;
   ```

## 🔄 Updating Your Space

```bash
# Make changes to your code
nano app.py

# Commit and push
git add .
git commit -m "Update: improved response quality"
git push hf main

# Space will automatically rebuild
```

## 🌐 Integration with VIJ Project

### API Endpoint

Your deployed space has an API:

```text
https://vishwas896-vish-ai.hf.space/api/predict
```

### Example from Next.js/v0.dev

```typescript
// lib/vishAI.ts
export async function chatWithVishAI(
  message: string,
  history: any[] = [],
  authToken: string = ""
) {
  const response = await fetch(
    "https://vishwas896-vish-ai.hf.space/api/predict",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        data: [message, history, authToken],
        fn_index: 0, // Chat function
      }),
    }
  );

  const result = await response.json();
  return result.data[0];
}
```

## 📧 Need Help?

- **Hugging Face Docs**: <https://huggingface.co/docs/hub/spaces>
- **Gradio Docs**: <https://gradio.app/docs>
- **Supabase Docs**: <https://supabase.com/docs>

---

### You're all set

🎉 Your Vish AI is now running on Hugging Face Spaces for free, integrated with Supabase, and ready to power your VIJ project!
