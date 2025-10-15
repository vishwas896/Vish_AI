"""
Test Vish AI locally before deploying to Hugging Face
Run: python test_local.py
"""

import os
import importlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🧪 Testing Vish AI Setup...")
print("-" * 50)

# Test 1: Environment Variables
print("\n1️⃣ Testing Environment Variables...")
supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if supabase_url and supabase_key:
    print(f"✅ Supabase URL: {supabase_url[:30]}...")
    print(f"✅ Supabase Key: {supabase_key[:30]}...")
else:
    print("❌ Missing environment variables!")
    print("   Make sure .env file exists with Supabase credentials")

# Test 2: Supabase Connection
print("\n2️⃣ Testing Supabase Connection...")
try:
    from supabase import create_client
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Supabase client created successfully")
    
    # Test database query (if table exists)
    try:
        result = supabase.table("vish_ai_logs").select("*").limit(1).execute()
        print(f"✅ Database query successful (found {len(result.data)} records)")
    except Exception as e:
        print(f"⚠️  Table might not exist yet: {e}")
        print("   Run the SQL in supabase_setup.sql to create the table")
        
except ImportError:
    print("❌ Supabase library not installed")
    print("   Run: pip install supabase")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")

# Test 3: Transformers Library
print("\n3️⃣ Testing Transformers Library...")
try:
    transformers_module = importlib.import_module("transformers")
    print(f"✅ Transformers version: {transformers_module.__version__}")
except ImportError:
    print("❌ Transformers not installed")
    print("   Run: pip install transformers")

# Test 4: PyTorch
print("\n4️⃣ Testing PyTorch...")
try:
    torch_module = importlib.import_module("torch")
    print(f"✅ PyTorch version: {torch_module.__version__}")
    cuda_available = torch_module.cuda.is_available()
    print(f"   CUDA available: {cuda_available}")
    device = "GPU" if cuda_available else "CPU"
    print(f"   Device: {device}")
except ImportError:
    print("❌ PyTorch not installed")
    print("   Run: pip install torch")

# Test 5: Gradio
print("\n5️⃣ Testing Gradio...")
try:
    import gradio as gr
    print(f"✅ Gradio version: {gr.__version__}")
except ImportError:
    print("❌ Gradio not installed")
    print("   Run: pip install gradio")

# Test 6: Model Loading (Quick Test)
print("\n6️⃣ Testing Model Loading (this may take a moment)...")
try:
    transformers_module = importlib.import_module("transformers")
    pipeline = getattr(transformers_module, "pipeline")
    print("   Loading DistilGPT2...")
    text_gen = pipeline("text-generation", model="distilgpt2", device=-1, max_length=50)
    print("✅ Model loaded successfully")
    
    # Quick inference test
    print("\n   Testing inference...")
    result = text_gen("Hello, Vish AI is", max_length=20, num_return_sequences=1)
    print(f"✅ Sample output: {result[0]['generated_text']}")
    
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    print("   This might be due to network issues or missing dependencies")

# Test 7: File Structure
print("\n7️⃣ Checking File Structure...")
required_files = [
    "app.py",
    "requirements.txt",
    "README.md",
    ".env",
    "supabase_setup.sql",
    "DEPLOYMENT.md"
]

for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - Missing!")

# Summary
print("\n" + "=" * 50)
print("🎯 Test Summary")
print("=" * 50)
print("""
Next steps:
1. If all tests pass, run: python app.py
2. Open browser to: http://localhost:7860
3. Test the chat, summarization, and sentiment features
4. When ready, deploy to Hugging Face using DEPLOYMENT.md

To deploy:
- Follow steps in DEPLOYMENT.md
- Push code to HF Space
- Add environment secrets
- Wait for build to complete
""")

print("\n✨ Testing complete! Check results above.\n")
