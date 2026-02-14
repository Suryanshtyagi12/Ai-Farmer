"""Test just the Groq vision API"""
from utils.llm_groq_vision_client import groq_vision_client
from PIL import Image

print("Testing Groq Llama 3.2 11B Vision...")
print("-" * 60)

# Create test image
test_img = Image.new('RGB', (200, 200), color=(100, 200, 100))
print("Test image created")

# Test Groq
print("\nCalling Groq API...")
response = groq_vision_client.get_vision_completion(
    prompt="What color is this image?",
    image_data=test_img,
    system_instruction="You are helpful. Be very brief."
)

print(f"\nResponse: {response}")

if "Error" in response:
    print("\n❌ Groq failed")
    exit(1)
else:
    print("\n✅ Groq working!")
    exit(0)
