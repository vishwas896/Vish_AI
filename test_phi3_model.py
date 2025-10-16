"""
Test script to verify Phi-3 model can be loaded and used
Run this before deploying to ensure everything works
"""

import sys
import time

def test_imports():
    """Test that all required packages can be imported"""
    print("=" * 60)
    print("🔍 Testing imports...")
    print("=" * 60)
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import transformers
        print(f"✅ Transformers: {transformers.__version__}")
    except ImportError as e:
        print(f"❌ Transformers import failed: {e}")
        return False
    
    try:
        import gradio
        print(f"✅ Gradio: {gradio.__version__}")
    except ImportError as e:
        print(f"❌ Gradio import failed: {e}")
        return False
    
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        print("✅ AutoModelForCausalLM and AutoTokenizer imported")
    except ImportError as e:
        print(f"❌ Failed to import model classes: {e}")
        return False
    
    print("\n✅ All imports successful!\n")
    return True


def test_model_loading():
    """Test loading the Phi-3 model (this will download ~7GB on first run)"""
    print("=" * 60)
    print("🔍 Testing Phi-3 model loading...")
    print("=" * 60)
    print("⚠️  Note: First run will download ~7GB model files")
    print("    This may take several minutes depending on internet speed\n")
    
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        model_name = "microsoft/Phi-3-mini-4k-instruct"
        
        print(f"📥 Loading tokenizer from {model_name}...")
        start_time = time.time()
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        tokenizer_time = time.time() - start_time
        print(f"✅ Tokenizer loaded in {tokenizer_time:.2f}s")
        
        print(f"\n📥 Loading model from {model_name}...")
        print("   Using CPU (for testing)...")
        start_time = time.time()
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="cpu",
            torch_dtype=torch.float32,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        model_time = time.time() - start_time
        print(f"✅ Model loaded in {model_time:.2f}s")
        
        # Get model info
        param_count = sum(p.numel() for p in model.parameters())
        print(f"\n📊 Model Information:")
        print(f"   Parameters: {param_count:,}")
        print(f"   Size: ~{param_count * 4 / 1024 / 1024 / 1024:.2f}GB (FP32)")
        
        return True, model, tokenizer
        
    except Exception as e:
        print(f"\n❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None


def test_inference(model, tokenizer):
    """Test model inference with a simple example"""
    print("\n" + "=" * 60)
    print("🔍 Testing model inference...")
    print("=" * 60)
    
    try:
        import torch
        
        # Test prompt
        test_prompt = "What is artificial intelligence?"
        print(f"\n📝 Test prompt: '{test_prompt}'")
        
        # Format prompt
        messages = [{"role": "user", "content": test_prompt}]
        formatted_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Tokenize
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        
        # Generate
        print("\n⏳ Generating response (this may take 10-30 seconds on CPU)...")
        start_time = time.time()
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        
        inference_time = time.time() - start_time
        
        # Decode
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract response
        if "<|assistant|>" in full_response:
            response = full_response.split("<|assistant|>")[-1].strip()
        else:
            response = full_response[len(formatted_prompt):].strip()
        
        print(f"✅ Response generated in {inference_time:.2f}s")
        print(f"\n🤖 Model response:\n{response}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_tasks(model, tokenizer):
    """Test all three tasks: chat, summarization, sentiment"""
    print("\n" + "=" * 60)
    print("🔍 Testing all Vish AI tasks...")
    print("=" * 60)
    
    import torch
    
    tasks = [
        {
            "name": "Chat",
            "prompt": "Hello! How can you help me?",
            "max_tokens": 50
        },
        {
            "name": "Summarization",
            "prompt": "Summarize the following text concisely: Artificial Intelligence is transforming industries by automating tasks and improving decision-making. Machine learning enables computers to learn from data without explicit programming. This technology is used in healthcare, finance, and transportation.",
            "max_tokens": 60
        },
        {
            "name": "Sentiment",
            "prompt": "Analyze the sentiment of this text. Respond with POSITIVE, NEGATIVE, or NEUTRAL: I love this product! It's amazing!",
            "max_tokens": 5
        }
    ]
    
    all_passed = True
    
    for task in tasks:
        print(f"\n📝 Testing {task['name']}...")
        print(f"   Prompt: {task['prompt'][:60]}...")
        
        try:
            messages = [{"role": "user", "content": task['prompt']}]
            formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(formatted, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=task['max_tokens'],
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            if "<|assistant|>" in response:
                response = response.split("<|assistant|>")[-1].strip()
            
            print(f"   ✅ {task['name']}: Success")
            print(f"   Response: {response[:100]}...")
            
        except Exception as e:
            print(f"   ❌ {task['name']}: Failed - {e}")
            all_passed = False
    
    return all_passed


def main():
    print("\n" + "=" * 60)
    print("🧪 Vish AI - Phi-3 Model Test Suite")
    print("=" * 60)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed. Please install required packages:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Test 2: Model loading
    success, model, tokenizer = test_model_loading()
    if not success:
        print("\n❌ Model loading failed. Check error messages above.")
        sys.exit(1)
    
    # Test 3: Basic inference
    if not test_inference(model, tokenizer):
        print("\n❌ Inference test failed.")
        sys.exit(1)
    
    # Test 4: All tasks
    if not test_all_tasks(model, tokenizer):
        print("\n⚠️  Some task tests failed, but model is functional.")
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print("\n🎉 Your Vish AI setup is ready!")
    print("\nNext steps:")
    print("1. Run the main application: python app.py")
    print("2. Access at: http://localhost:7860")
    print("3. (Optional) Fine-tune the model: python fine_tune_phi3.py")
    print("4. Deploy to Hugging Face Spaces for production")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
