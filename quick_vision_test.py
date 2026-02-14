"""Quick test for the updated vision models"""
import sys

print("Testing updated vision models...")
print("-" * 60)

try:
    from utils.unified_vision_handler import unified_vision_handler
    from PIL import Image
    
    # Create test image
    test_img = Image.new('RGB', (200, 200), color=(100, 200, 100))
    print("✅ Test image created")
    
    # Test the vision handler
    print("\nTesting vision APIs:")
    print("  - Groq: llama-3.2-11b-vision-preview")
    print("  - Gemini: gemini-1.5-flash")
    print()
    
    response, api_used = unified_vision_handler.get_vision_response(
        prompt="What do you see in this image? Describe the color.",
        image_data=test_img,
        system_instruction="You are a helpful assistant. Be brief."
    )
    
    if "Error" in response or "failed" in response:
        print(f"\n❌ FAILED: {response}")
        sys.exit(1)
    else:
        print(f"\n✅ SUCCESS!")
        print(f"   API used: {api_used}")
        print(f"   Response: {response[:150]}...")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
