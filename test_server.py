"""
Vish AI - Simple Test Server (for local dev container testing)
This is a lightweight version for testing in Python 3.14
The full AI version will run on Hugging Face Spaces (Python 3.10/3.11)
"""

import gradio as gr
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "https://lyebtceryednzafhyunq.supabase.co")

def simple_chat(message: str, history: list) -> str:
    """Simple echo chatbot for testing"""
    return f"✅ Vish AI is running!\n\nYou said: {message}\n\n💡 Note: This is a test version. AI models require PyTorch which isn't available in Python 3.14.\n\n🚀 For the full AI experience, deploy to Hugging Face Spaces (Python 3.10/3.11) using the instructions in DEPLOYMENT.md"

def simple_summarize(text: str) -> str:
    """Simple summarizer for testing"""
    word_count = len(text.split())
    return f"✅ Text received: {word_count} words\n\nFirst 100 chars: {text[:100]}...\n\n🚀 Full summarization available on Hugging Face Spaces"

def simple_sentiment(text: str) -> str:
    """Simple sentiment for testing"""
    positive_words = ['good', 'great', 'excellent', 'happy', 'love', 'wonderful', 'amazing']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad', 'horrible', 'worst']
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return "😊 **POSITIVE** (Simple keyword detection)\n\n🚀 Full sentiment analysis available on Hugging Face Spaces"
    elif neg_count > pos_count:
        return "😞 **NEGATIVE** (Simple keyword detection)\n\n🚀 Full sentiment analysis available on Hugging Face Spaces"
    else:
        return "😐 **NEUTRAL** (Simple keyword detection)\n\n🚀 Full sentiment analysis available on Hugging Face Spaces"

# Create Gradio Interface
with gr.Blocks(theme=gr.themes.Soft(), title="Vish AI - Test Server") as demo:
    gr.Markdown("""
    # 🌟 Vish AI - Test Server
    ### Local Development Environment
    
    ⚠️ **This is a simplified test version for Python 3.14 dev container.**
    
    The full AI-powered version with DistilGPT2, DistilBART, and DistilBERT will run on **Hugging Face Spaces**.
    
    📖 See `DEPLOYMENT.md` for deployment instructions.
    """)
    
    gr.Markdown(f"""
    ### 🔗 Connected to Supabase
    - **URL**: {SUPABASE_URL}
    - **Status**: ✅ Environment loaded
    """)
    
    with gr.Tabs():
        # Chat Tab
        with gr.Tab("💬 Chat Test"):
            chatbot = gr.Chatbot(height=400, label="Test Chat")
            msg = gr.Textbox(
                label="Your Message",
                placeholder="Type something to test...",
                lines=2
            )
            with gr.Row():
                submit = gr.Button("Send", variant="primary")
                clear = gr.Button("Clear")
            
            msg.submit(simple_chat, [msg, chatbot], chatbot)
            submit.click(simple_chat, [msg, chatbot], chatbot)
            clear.click(lambda: None, None, chatbot, queue=False)
        
        # Summarization Tab
        with gr.Tab("📝 Summarization Test"):
            with gr.Row():
                with gr.Column():
                    input_text = gr.Textbox(
                        label="Enter Text",
                        placeholder="Paste your text here...",
                        lines=10
                    )
                    summarize_btn = gr.Button("Test Summarize", variant="primary")
                
                with gr.Column():
                    summary_output = gr.Textbox(
                        label="Summary Result",
                        lines=10
                    )
            
            summarize_btn.click(simple_summarize, input_text, summary_output)
        
        # Sentiment Analysis Tab
        with gr.Tab("😊 Sentiment Test"):
            with gr.Row():
                with gr.Column():
                    sentiment_input = gr.Textbox(
                        label="Enter Text",
                        placeholder="How do you feel?",
                        lines=5
                    )
                    analyze_btn = gr.Button("Test Sentiment", variant="primary")
                
                with gr.Column():
                    sentiment_output = gr.Textbox(
                        label="Sentiment Result",
                        lines=5
                    )
            
            analyze_btn.click(simple_sentiment, sentiment_input, sentiment_output)
        
        # Info Tab
        with gr.Tab("ℹ️ Info"):
            gr.Markdown("""
            ## 🛠️ Development Environment
            
            **Current Setup:**
            - Python 3.14.0 (dev container)
            - Gradio ✅ Installed
            - Supabase ✅ Configured
            - PyTorch ❌ Not available (Python 3.14)
            
            **For Full AI Features:**
            1. Deploy to Hugging Face Spaces
            2. Hugging Face uses Python 3.10/3.11
            3. PyTorch and AI models will work there
            
            **Files Ready for Deployment:**
            - ✅ `app.py` - Full AI application
            - ✅ `requirements.txt` - Dependencies
            - ✅ `.env` - Configuration
            - ✅ `DEPLOYMENT.md` - Instructions
            - ✅ `supabase_setup.sql` - Database schema
            
            ## 🚀 Next Steps
            
            1. Test this interface
            2. Follow `DEPLOYMENT.md` to deploy to HF Spaces
            3. Add secrets in HF Space settings
            4. Run `supabase_setup.sql` in Supabase
            5. Enjoy full AI features!
            
            ---
            
            **VIJ Project** | Powered by Supabase & Hugging Face
            """)
    
    gr.Markdown("""
    ---
    🔗 **Quick Links:**
    - [Hugging Face Space](https://huggingface.co/spaces/Vishwas896/Vish-AI)
    - [Supabase Dashboard](https://supabase.com/dashboard/project/lyebtceryednzafhyunq)
    - [DEPLOYMENT.md](./DEPLOYMENT.md)
    """)

if __name__ == "__main__":
    print("🚀 Starting Vish AI Test Server...")
    print("📍 This is a simplified version for local testing")
    print("🎯 Full AI features available on Hugging Face Spaces")
    print("")
    demo.queue()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
