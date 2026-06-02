# test_env.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load from project root
env_path = Path(__file__).parent / ".env"
print(f"🔍 Looking for .env at: {env_path}")
print(f"📁 File exists: {env_path.exists()}")

# Load and check
load_dotenv(env_path)

groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

print(f"\n🔑 GROQ_API_KEY loaded: {'✅ YES' if groq_key else '❌ NO'}")
print(f"🔑 TAVILY_API_KEY loaded: {'✅ YES' if tavily_key else '❌ NO'}")

if tavily_key:
    print(f"   Key starts with: {tavily_key[:8]}...")
else:
    print("   💡 Tip: Make sure TAVILY_API_KEY has no spaces/quotes in .env")