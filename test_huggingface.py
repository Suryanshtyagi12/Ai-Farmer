"""Test HuggingFace BLIP vision model"""
from utils.llm_huggingface_vision_client import huggingface_vision_client
from PIL import Image

print("Testing HuggingFace BLIP Vision Model (FREE)")
print("-" * 60)

# Create test image
test_img = Image.new('RGB', (200, 200), color=(100, 200, 100))
print("Test image created (green color)")

# Test the vision model
print("\nCalling HuggingFace BLIP API...")
print("Question: What color is this image?")

response = huggingface_vision_client.get_vision_completion(
    prompt="What color is this image?",
    image_data=test_img
)

print(f"\nResponse: {response}")

if "Error" in response:
    print("\nStatus: FAILED")
else:
    print("\nStatus: SUCCESS!")
