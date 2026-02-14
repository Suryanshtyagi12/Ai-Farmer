"""List all available Groq models"""
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("=" * 60)
print("Available Groq Models (February 2026):")
print("=" * 60)

try:
    models = client.models.list()
    vision_models = []
    
    for model in models.data:
        print(f"\n- {model.id}")
        # Check if it's a vision model (usually has 'vision' in the name or context window)
        if 'vision' in model.id.lower() or 'llava' in model.id.lower() or 'pixtral' in model.id.lower():
            vision_models.append(model.id)
            print("  *** VISION MODEL ***")
    
    print("\n" + "=" * 60)
    print("VISION MODELS FOUND:")
    for vm in vision_models:
        print(f"  ✅ {vm}")
    
except Exception as e:
    print(f"Error: {e}")
