"""Simple test to check if vision APIs are working"""
import sys
print("Starting vision API test...")
print("-" * 60)

# Test 1: Check if modules can be imported
print("\n[Test 1] Importing modules...")
try:
    from utils.unified_vision_handler import unified_vision_handler
    print("✅ unified_vision_handler imported successfully")
except Exception as e:
    print(f"❌ Failed to import unified_vision_handler: {e}")
    sys.exit(1)

try:
    from PIL import Image
    print("✅ PIL imported successfully")
except Exception as e:
    print(f"❌ Failed to import PIL: {e}")
    sys.exit(1)

# Test 2: Create a simple test image
print("\n[Test 2] Creating test image...")
try:
    test_img = Image.new('RGB', (200, 200), color=(100, 150, 200))
    print(f"✅ Test image created: {test_img.size}, {test_img.mode}")
except Exception as e:
    print(f"❌ Failed to create image: {e}")
    sys.exit(1)

# Test 3: Test the vision handler
print("\n[Test 3] Testing vision handler...")
print("Calling unified_vision_handler.get_vision_response()...")
try:
    response, api_used = unified_vision_handler.get_vision_response(
        prompt="What colors do you see in this image?",
        image_data=test_img,
        system_instruction="You are a helpful assistant."
    )
    print(f"\n✅ Got response from API: {api_used}")
    print(f"\nResponse preview (first 300 chars):")
    print(response[:300])
    print("\n" + "=" * 60)
    print("SUCCESS! Vision API system is working!")
    print("=" * 60)
except Exception as e:
    print(f"\n❌ Error during API call: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
