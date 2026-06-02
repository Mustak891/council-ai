# test_groq.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables from .env
load_dotenv()

# Get your API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ GROQ_API_KEY not found in .env file")
    exit(1)

print(f"✅ API Key loaded (starts with: {api_key[:8]}...)")

# Try available models in order
models_to_try = [
    "llama-3.3-70b-specdec",
    "llama-3.3-70b-versatile", 
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

for model_name in models_to_try:
    try:
        print(f"\n🔄 Testing model: {model_name}")
        llm = ChatGroq(model=model_name, temperature=0.5, api_key=api_key)
        response = llm.invoke("Say 'Hello from Groq!' in one sentence.")
        print(f"✅ SUCCESS with {model_name}:")
        print(f"   Response: {response.content.strip()}")
        print(f"\n🎯 UPDATE your agents.py to use: '{model_name}'")
        break
    except Exception as e:
        print(f"❌ Failed with {model_name}: {str(e)[:100]}...")
else:
    print("\n💥 All models failed. Check your API key or Groq dashboard.")