"""
VISH AI - Enhanced Gradio UI
Multi-tab interface with dataset stats and improvement tracking
"""

import gradio as gr
from typing import List, Tuple
import time
from datetime import datetime

from app.model_handler import get_model_handler
from app.dataset_manager import get_dataset_manager
from app.retrain import run_training_pipeline


def chat_interface(message: str, history: List, category: str = "assistant") -> Tuple[List, str]:
    """Chat interface with category selection"""
    if not message.strip():
        return history, ""
    
    try:
        start_time = time.time()
        
        # Get model handler
        model_handler = get_model_handler()
        
        # System prompts for different categories
        system_prompts = {
            "assistant": None,
            "resume": "You are an expert resume builder and career advisor. Help create professional, ATS-friendly resumes.",
            "research": "You are a knowledgeable research assistant. Provide accurate, well-researched information.",
            "business": "You are a business consultant. Provide strategic advice for business growth and management."
        }
        
        # Generate response
        response = model_handler.generate_response(
            prompt=message,
            max_new_tokens=300,
            temperature=0.7,
            system_prompt=system_prompts.get(category)
        )
        
        elapsed_time = time.time() - start_time
        
        # Save to dataset
        dataset_mgr = get_dataset_manager()
        interaction_id = dataset_mgr.add_interaction(
            user_prompt=message,
            ai_response=response,
            category=category,
            metadata={
                "response_time": elapsed_time,
                "model_version": model_handler.model_version,
                "interface": "gradio"
            }
        )
        
        # Format response with metadata
        formatted_response = f"{response}\n\n⚡ *Response time: {elapsed_time:.2f}s | ID: {interaction_id[:8]}*"
        
        history.append((message, formatted_response))
        return history, ""
        
    except Exception as e:
        history.append((message, f"❌ Error: {str(e)}"))
        return history, ""


def submit_feedback(interaction_id: str, score: int, comment: str) -> str:
    """Submit feedback for an interaction"""
    try:
        if not interaction_id.strip():
            return "⚠️ Please enter an interaction ID"
        
        dataset_mgr = get_dataset_manager()
        dataset_mgr.add_feedback(
            interaction_id=interaction_id,
            score=score,
            comment=comment if comment.strip() else None
        )
        
        return f"✅ Feedback submitted! Score: {score}/5"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_stats_display() -> str:
    """Get formatted dataset statistics"""
    try:
        dataset_mgr = get_dataset_manager()
        model_handler = get_model_handler()
        
        stats = dataset_mgr.get_dataset_stats()
        model_info = model_handler.get_model_info()
        
        # Format statistics
        display = f"""
## 📊 VISH AI Statistics

### Model Information
- **Current Version**: {model_info['current_version']}
- **Base Model**: {model_info['base_model']}
- **Device**: {model_info['device']}
- **Fine-tuned**: {'✅ Yes' if model_info['fine_tuned'] else '❌ Not yet'}

### Dataset Statistics
- **Total Interactions**: {stats['total_interactions']:,}
- **Total Feedback**: {stats['total_feedback']}
- **Average Rating**: {stats['avg_feedback_score']:.2f}/5.0 ⭐
- **Research Data**: {stats['total_research']}

### By Category
"""
        
        for category, count in stats['by_category'].items():
            display += f"- **{category.title()}**: {count}\n"
        
        if stats['last_updated']:
            display += f"\n**Last Updated**: {stats['last_updated']}\n"
        
        # Training metadata
        if 'metadata' in model_info and model_info['metadata']['training_runs'] > 0:
            meta = model_info['metadata']
            display += f"""
### Training History
- **Training Runs**: {meta['training_runs']}
- **Dataset Size**: {meta['dataset_size']}
- **Last Trained**: {meta['last_updated'] or 'Never'}
"""
        
        return display
        
    except Exception as e:
        return f"❌ Error loading stats: {str(e)}"


def trigger_training(min_samples: int, epochs: int, admin_key: str) -> str:
    """Trigger model retraining"""
    try:
        import os
        if admin_key != os.getenv("VISH_ADMIN_KEY", "vish-admin-2024"):
            return "❌ Invalid admin key"
        
        result = run_training_pipeline(
            min_samples=min_samples,
            epochs=epochs
        )
        
        if result["status"] == "success":
            return f"""
✅ **Training Completed Successfully!**

- **New Version**: {result['version']}
- **Training Loss**: {result['metrics']['train_loss']:.4f}
- **Samples Used**: {result['metrics']['samples']}
- **Epochs**: {result['metrics']['epochs']}

The model has been automatically reloaded with the new version.
"""
        elif result["status"] == "skipped":
            return f"⚠️ **Training Skipped**: {result['reason']}\n\nSamples: {result['samples']}/{result['required']}"
        else:
            return f"❌ **Training Failed**: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"


def create_gradio_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(
        theme=gr.themes.Soft(),
        title="VISH AI - Self-Training Assistant",
        css=".gradio-container {max-width: 1200px !important}"
    ) as demo:
        
        gr.Markdown("""
        # 🌟 VISH AI - Self-Improving AI Assistant
        ### Powered by Microsoft Phi-3 Mini with Continuous Learning
        
        **Features**: Chat Assistant | Resume Builder | Research | Business Consulting | Auto-Training
        """)
        
        with gr.Tabs():
            # Tab 1: Chat Assistant
            with gr.Tab("💬 VISH Assistant"):
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            height=500,
                            label="VISH AI Chat",
                            type="tuples",
                            show_copy_button=True
                        )
                        with gr.Row():
                            msg = gr.Textbox(
                                label="Your Message",
                                placeholder="Ask me anything...",
                                lines=3,
                                scale=4
                            )
                        with gr.Row():
                            category = gr.Dropdown(
                                choices=["assistant", "resume", "research", "business"],
                                value="assistant",
                                label="Category",
                                scale=1
                            )
                            submit = gr.Button("Send", variant="primary", scale=1)
                            clear = gr.Button("Clear", scale=1)
                    
                    with gr.Column(scale=1):
                        gr.Markdown("""
                        **Usage Tips:**
                        - Select a category for specialized assistance
                        - All conversations help train the AI
                        - Provide feedback to improve quality
                        
                        **Categories:**
                        - 🤖 **Assistant**: General chat
                        - 📝 **Resume**: Career advice
                        - 🔬 **Research**: Information gathering
                        - 💼 **Business**: Strategy & consulting
                        """)
                
                # Handle chat
                def respond(message, history, cat):
                    return chat_interface(message, history or [], cat)
                
                submit.click(respond, inputs=[msg, chatbot, category], outputs=[chatbot, msg])
                msg.submit(respond, inputs=[msg, chatbot, category], outputs=[chatbot, msg])
                clear.click(lambda: [], None, chatbot, queue=False)
            
            # Tab 2: Feedback & Rating
            with gr.Tab("⭐ Feedback"):
                gr.Markdown("""
                ## Help VISH AI Improve!
                
                Your feedback trains the AI to give better responses. Rate your interactions below.
                """)
                
                with gr.Row():
                    with gr.Column():
                        feedback_id = gr.Textbox(
                            label="Interaction ID",
                            placeholder="Enter the ID from your chat response (e.g., a1b2c3d4)",
                            lines=1
                        )
                        feedback_score = gr.Slider(
                            minimum=1,
                            maximum=5,
                            step=1,
                            value=5,
                            label="Rating (1=Poor, 5=Excellent)"
                        )
                        feedback_comment = gr.Textbox(
                            label="Comments (Optional)",
                            placeholder="What did you like or dislike?",
                            lines=3
                        )
                        feedback_btn = gr.Button("Submit Feedback", variant="primary")
                    
                    with gr.Column():
                        feedback_result = gr.Textbox(
                            label="Result",
                            lines=5,
                            interactive=False
                        )
                
                feedback_btn.click(
                    submit_feedback,
                    inputs=[feedback_id, feedback_score, feedback_comment],
                    outputs=feedback_result
                )
            
            # Tab 3: Dataset & Statistics
            with gr.Tab("📊 Statistics"):
                gr.Markdown("## Dataset & Model Statistics")
                
                stats_display = gr.Markdown(get_stats_display())
                refresh_btn = gr.Button("🔄 Refresh Stats", variant="secondary")
                
                refresh_btn.click(
                    get_stats_display,
                    outputs=stats_display
                )
            
            # Tab 4: Admin - Training
            with gr.Tab("🎓 Training (Admin)"):
                gr.Markdown("""
                ## Self-Training Control Panel
                
                ⚠️ **Admin Only** - Trigger model retraining with collected data
                """)
                
                with gr.Row():
                    with gr.Column():
                        train_min_samples = gr.Slider(
                            minimum=5,
                            maximum=100,
                            step=5,
                            value=10,
                            label="Minimum Samples Required"
                        )
                        train_epochs = gr.Slider(
                            minimum=1,
                            maximum=10,
                            step=1,
                            value=3,
                            label="Training Epochs"
                        )
                        train_admin_key = gr.Textbox(
                            label="Admin Key",
                            type="password",
                            placeholder="Enter admin key"
                        )
                        train_btn = gr.Button("🚀 Start Training", variant="primary", size="lg")
                    
                    with gr.Column():
                        train_result = gr.Textbox(
                            label="Training Result",
                            lines=15,
                            interactive=False
                        )
                
                train_btn.click(
                    trigger_training,
                    inputs=[train_min_samples, train_epochs, train_admin_key],
                    outputs=train_result
                )
            
            # Tab 5: Model Info & Guide
            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
                ## 🤖 VISH AI - Self-Improving Assistant
                
                ### How It Works
                
                1. **You Chat** → All conversations are automatically saved
                2. **You Rate** → Provide feedback on response quality (1-5 stars)
                3. **AI Learns** → High-rated interactions train the model
                4. **AI Improves** → Model gets better at understanding your needs
                
                ### Technology Stack
                
                - **Base Model**: Microsoft Phi-3 Mini 4K Instruct (3.8B parameters)
                - **Fine-tuning**: LoRA (Low-Rank Adaptation) for efficient training
                - **Framework**: Hugging Face Transformers + PEFT
                - **Backend**: FastAPI for API endpoints
                - **Frontend**: Gradio for interactive UI
                - **Storage**: Local JSONL files (lightweight & portable)
                
                ### Data Collection
                
                VISH AI collects:
                - User prompts and AI responses
                - Response quality ratings (1-5 stars)
                - Interaction categories (assistant, resume, research, business)
                - Response times and model versions
                
                All data is stored locally and used **only** to improve your personal AI assistant.
                
                ### Training Process
                
                1. System collects interactions with ratings ≥ 3 stars
                2. Data is cleaned and deduplicated
                3. Phi-3 model is fine-tuned with LoRA adapters
                4. New model version is saved and automatically loaded
                5. Improvement metrics are tracked
                
                ### API Endpoints
                
                - `POST /api/chat` - Send chat messages
                - `POST /api/feedback` - Submit ratings
                - `POST /api/admin/retrain` - Trigger training (admin)
                - `GET /api/stats` - Get dataset statistics
                - `GET /health` - System health check
                
                ### Model Versions
                
                Each training run creates a new model version (e.g., `v20241016_143022`).
                The system automatically uses the latest trained version.
                
                ---
                
                **Built with ❤️ by Vishwas | VIJ Project**
                """)
        
        return demo


# For standalone Gradio testing
if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860)
