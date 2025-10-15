"""
Vish AI - Virtual Intelligent System Hub
Lightweight multimodal AI assistant optimized for Hugging Face Spaces
Production-ready version
"""

import gradio as gr
import os
from datetime import datetime
import time
import importlib

# Supabase imports
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ Supabase not available - running in demo mode")

# AI model imports (lazy loading for better performance)
pipeline = None
torch = None

try:
    pipeline = getattr(importlib.import_module("transformers"), "pipeline", None)
    torch = importlib.import_module("torch")
    AI_AVAILABLE = pipeline is not None
except ImportError:
    AI_AVAILABLE = False
    pipeline = None
    torch = None

if not AI_AVAILABLE:
    print("⚠️ AI models not available - using fallback mode")

# Supabase configuration
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "https://lyebtceryednzafhyunq.supabase.co")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")

# Initialize Supabase client
supabase = None
if SUPABASE_AVAILABLE and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase connected successfully")
    except Exception as e:
        print(f"⚠️ Supabase initialization error: {e}")
else:
    print("⚠️ Supabase credentials not configured")

# Global variables for models
text_generator = None
summarizer = None
sentiment_analyzer = None

def initialize_models():
    """Initialize lightweight AI models optimized for CPU"""
    global text_generator, summarizer, sentiment_analyzer
    
    if not AI_AVAILABLE:
        print("⚠️ AI libraries not available - using demo mode")
        return False
    
    try:
        # Use DistilGPT2 - very lightweight (82MB) and fast
        print("📥 Loading text generation model (DistilGPT2)...")
        text_generator = pipeline(
            "text-generation",
            model="distilgpt2",
            device=-1,  # CPU
            max_length=150
        )
        print("✅ Text generation model loaded")
        
        # Lightweight summarization model (~300MB)
        print("📥 Loading summarization model (DistilBART)...")
        summarizer = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-6-6",
            device=-1
        )
        print("✅ Summarization model loaded")
        
        # Sentiment analysis - very lightweight
        print("📥 Loading sentiment analyzer (DistilBERT)...")
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1
        )
        print("✅ Sentiment analyzer loaded")
        
        print("🎉 All models loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return False

def verify_user_token(token: str) -> dict:
    """Verify Supabase user authentication token"""
    if not supabase or not token:
        return {"authenticated": False, "user": None}
    
    try:
        user = supabase.auth.get_user(token)
        return {"authenticated": True, "user": user.user.email if user.user else None}
    except Exception as e:
        return {"authenticated": False, "error": str(e)}

def log_interaction(user_email: str, prompt: str, response: str, model_type: str):
    """Log user interactions to Supabase"""
    if not supabase:
        return
    
    try:
        data = {
            "user_email": user_email,
            "prompt": prompt,
            "response": response,
            "model_type": model_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        supabase.table("vish_ai_logs").insert(data).execute()
    except Exception as e:
        print(f"Logging error: {e}")

def chat_with_vish(message: str, history: list, auth_token: str = "") -> str:
    """Main chat function with authentication"""
    
    # Verify authentication (optional - remove if you want public access)
    user_info = verify_user_token(auth_token) if auth_token else {"authenticated": False}
    user_email = user_info.get("user", "anonymous")
    
    if not AI_AVAILABLE or not text_generator:
        # Fallback response when AI is not available
        fallback = "🤖 **Vish AI (Demo Mode)**\n\nYou said: _{}_\n\n⚠️ AI models are not loaded. This happens when:\n- Running in Python 3.14 (PyTorch not supported)\n- First deployment (models downloading)\n\n✅ **This will work perfectly on Hugging Face Spaces!**\n\n_Response time: <0.1s_".format(message)
        history.append([message, fallback])
        return history
    
    try:
        # Generate response using DistilGPT2
        start_time = time.time()
        
        # Build context from history
        context = ""
        if history:
            for h in history[-3:]:  # Last 3 exchanges for context
                context += f"User: {h[0]}\nAssistant: {h[1]}\n"
        
        prompt = f"{context}User: {message}\nAssistant:"
        
        response = text_generator(
            prompt,
            max_length=len(prompt.split()) + 50,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=50256
        )[0]['generated_text']
        
        # Extract only the new response
        assistant_response = response.split("Assistant:")[-1].strip()
        
        # Clean up response
        if "User:" in assistant_response:
            assistant_response = assistant_response.split("User:")[0].strip()
        
        elapsed_time = time.time() - start_time
        
        # Log interaction
        log_interaction(user_email, message, assistant_response, "chat")
        
        final_response = f"{assistant_response}\n\n⚡ _Response time: {elapsed_time:.2f}s_"
        history.append([message, final_response])
        return history
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        history.append([message, error_msg])
        return history

def summarize_text(text: str, auth_token: str = "") -> str:
    """Summarize long text"""
    user_info = verify_user_token(auth_token) if auth_token else {"authenticated": False}
    user_email = user_info.get("user", "anonymous")
    
    if not AI_AVAILABLE or not summarizer:
        # Fallback summary
        word_count = len(text.split())
        return f"📝 **Summary (Demo Mode)**\n\nReceived {word_count} words.\n\nFirst 150 characters:\n_{text[:150]}_...\n\n⚠️ Full AI summarization available on Hugging Face Spaces!\n\n_Processing time: <0.1s_"
    
    try:
        if len(text.split()) < 50:
            return "⚠️ Text is too short to summarize. Please provide at least 50 words."
        
        start_time = time.time()
        
        # Truncate if too long (model limit)
        max_length = 1024
        if len(text.split()) > max_length:
            text = " ".join(text.split()[:max_length])
        
        summary = summarizer(
            text,
            max_length=130,
            min_length=30,
            do_sample=False
        )[0]['summary_text']
        
        elapsed_time = time.time() - start_time
        
        log_interaction(user_email, text[:100], summary, "summarization")
        
        return f"{summary}\n\n⚡ _Processing time: {elapsed_time:.2f}s_"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

def analyze_sentiment(text: str, auth_token: str = "") -> str:
    """Analyze sentiment of text"""
    user_info = verify_user_token(auth_token) if auth_token else {"authenticated": False}
    user_email = user_info.get("user", "anonymous")
    
    if not AI_AVAILABLE or not sentiment_analyzer:
        # Simple fallback sentiment
        positive_words = ['good', 'great', 'excellent', 'happy', 'love', 'wonderful', 'amazing', 'fantastic', 'brilliant']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad', 'horrible', 'worst', 'poor', 'disappointing']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            emoji, label, score = "😊", "POSITIVE", 0.85
        elif neg_count > pos_count:
            emoji, label, score = "😞", "NEGATIVE", 0.85
        else:
            emoji, label, score = "😐", "NEUTRAL", 0.50
        
        return f"{emoji} **{label}** (Demo - Simple keyword detection)\n\nConfidence: ~{score:.0%}\n\n⚠️ Full AI sentiment analysis available on Hugging Face Spaces!\n\n_Analysis time: <0.1s_"
    
    try:
        start_time = time.time()
        
        result = sentiment_analyzer(text[:512])[0]  # Limit to 512 chars
        
        label = result['label']
        score = result['score']
        
        emoji = "😊" if label == "POSITIVE" else "😞"
        
        elapsed_time = time.time() - start_time
        
        log_interaction(user_email, text[:100], f"{label}: {score:.2%}", "sentiment")
        
        return f"{emoji} **{label}** (Confidence: {score:.2%})\n\n⚡ _Analysis time: {elapsed_time:.2f}s_"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_model_info() -> str:
    """Get information about loaded models"""
    info = """
    ## 🤖 Vish AI - Active Models
    
    **Chat Assistant:**
    - Model: DistilGPT2 (~82MB)
    - Speed: ~0.5-2s per response
    - Use: Natural conversation
    
    **Text Summarizer:**
    - Model: DistilBART-CNN (~300MB)
    - Speed: ~1-3s per summary
    - Use: Condense long articles
    
    **Sentiment Analyzer:**
    - Model: DistilBERT-SST2 (~255MB)
    - Speed: ~0.3-1s per analysis
    - Use: Detect positive/negative sentiment
    
    **Total Memory:** ~650MB
    **Optimized for:** CPU inference on free tier
    """
    return info

# Initialize models on startup
print("=" * 60)
print("🚀 Initializing Vish AI - Production Ready")
print("=" * 60)
print(f"Python Version: 3.x")
print(f"AI Available: {AI_AVAILABLE}")
print(f"Supabase Available: {SUPABASE_AVAILABLE}")
print("=" * 60)

if AI_AVAILABLE:
    print("\n🔄 Starting model initialization...")
    models_loaded = initialize_models()
    if models_loaded:
        print("\n✅ All systems ready!")
    else:
        print("\n⚠️ Running in demo mode")
else:
    print("\n⚠️ AI libraries not available - running in demo mode")
    print("💡 This is normal for Python 3.14 - deploy to Hugging Face Spaces for full AI!")

print("=" * 60)

# Create Gradio Interface
with gr.Blocks(theme=gr.themes.Soft(), title="Vish AI") as demo:
    # Dynamic header based on AI availability
    if AI_AVAILABLE and text_generator:
        status_badge = "🟢 **PRODUCTION** - All AI Models Active"
    else:
        status_badge = "🟡 **DEMO MODE** - Deploy to Hugging Face for Full AI"
    
    gr.Markdown(f"""
    # 🌟 Vish AI - Virtual Intelligent System Hub
    ### Lightweight, Fast, Multimodal AI Assistant
    
    {status_badge}
    
    Optimized for Hugging Face Spaces | Powered by Supabase
    """)
    
    with gr.Tabs():
        # Chat Tab
        with gr.Tab("💬 Chat Assistant"):
            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(height=400, label="Vish AI Chat", type="tuples")
                    msg = gr.Textbox(
                        label="Your Message",
                        placeholder="Ask me anything...",
                        lines=2
                    )
                    with gr.Row():
                        submit = gr.Button("Send", variant="primary")
                        clear = gr.Button("Clear")
                
                with gr.Column(scale=1):
                    auth_token_chat = gr.Textbox(
                        label="🔐 Auth Token (Optional)",
                        type="password",
                        placeholder="Supabase JWT token",
                        lines=3
                    )
                    gr.Markdown("""
                    **Usage Tips:**
                    - Just type and chat!
                    - No token needed for demo
                    - Add token for logging
                    """)
            
            def respond(message, history, token):
                return chat_with_vish(message, history or [], token)
            
            submit.click(respond, inputs=[msg, chatbot, auth_token_chat], outputs=chatbot)
            msg.submit(respond, inputs=[msg, chatbot, auth_token_chat], outputs=chatbot)
            clear.click(lambda: [], None, chatbot, queue=False)
        
        # Summarization Tab
        with gr.Tab("📝 Text Summarizer"):
            with gr.Row():
                with gr.Column():
                    input_text = gr.Textbox(
                        label="Enter Text to Summarize",
                        placeholder="Paste your long text here (minimum 50 words)...",
                        lines=10
                    )
                    auth_token_sum = gr.Textbox(
                        label="Auth Token (Optional)",
                        type="password"
                    )
                    summarize_btn = gr.Button("Summarize", variant="primary")
                
                with gr.Column():
                    summary_output = gr.Textbox(
                        label="Summary",
                        lines=10
                    )
            
            summarize_btn.click(summarize_text, [input_text, auth_token_sum], summary_output)
        
        # Sentiment Analysis Tab
        with gr.Tab("😊 Sentiment Analysis"):
            with gr.Row():
                with gr.Column():
                    sentiment_input = gr.Textbox(
                        label="Enter Text to Analyze",
                        placeholder="How do you feel about this?",
                        lines=5
                    )
                    auth_token_sent = gr.Textbox(
                        label="Auth Token (Optional)",
                        type="password"
                    )
                    analyze_btn = gr.Button("Analyze Sentiment", variant="primary")
                
                with gr.Column():
                    sentiment_output = gr.Textbox(
                        label="Sentiment Result",
                        lines=5
                    )
            
            analyze_btn.click(analyze_sentiment, [sentiment_input, auth_token_sent], sentiment_output)
        
        # Model Info Tab
        with gr.Tab("ℹ️ Model Info"):
            gr.Markdown(get_model_info())
    
    gr.Markdown("""
    ---
    **VIJ Project** | Powered by Supabase & Hugging Face | Built with ❤️ by Vishwas
    """)

# Launch the app
if __name__ == "__main__":
    demo.queue()  # Enable queuing for better performance
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
