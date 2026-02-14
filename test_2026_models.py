"""Test the updated vision models"""
from utils.unified_vision_handler import unified_vision_handler
from PIL import Image

print("Testing CURRENT vision models (2026):")
print("  - Groq: llava-v1.5-7b-4096-preview")
print("  - Gemini: gemini-2.0-flash-exp")
print("-" * 60)

# Create test image
test_img = Image.new('RGB', (200, 200), color=(100, 200, 100))
print("\nTest image created (green color)")

# Test the vision handler
print("\nCalling unified vision handler...")
response, api_used = unified_vision_handler.get_vision_response(
    prompt="What color is this image?",
    image_data=test_img,
    system_instruction="You are helpful. Be very brief, just say the color."
)

print(f"\nAPI used: {api_used}")
print(f"Response: {response}")

if "Error" in response or "failed" in response:
    print("\nStatus: FAILED")
else:
    print("\nStatus: SUCCESS!")
