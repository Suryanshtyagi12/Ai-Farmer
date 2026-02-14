"""List available Gemini models to find the correct vision model name"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not found")
    exit(1)

genai.configure(api_key=api_key)

print("=" * 60)
print("Available Gemini Models:")
print("=" * 60)

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"\n✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Supports: {', '.join(model.supported_generation_methods)}")
except Exception as e:
    print(f"❌ Error: {e}")
