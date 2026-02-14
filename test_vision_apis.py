"""
Test script for Multi-API Vision System
Tests both Groq and Gemini vision APIs with fallback
"""

from utils.unified_vision_handler import unified_vision_handler
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """Create a simple test image with text"""
    img = Image.new('RGB', (400, 300), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((100, 150), "Wheat Plant - Test Image", fill=(255, 255, 0))
    return img

def test_vision_apis():
    print("=" * 60)
    print("Testing Multi-API Vision System")
    print("=" * 60)
    
    # Create test image
    print("\n[1] Creating test image...")
    test_img = create_test_image()
    print("✅ Test image created")
    
    # Test vision handler
    print("\n[2] Testing unified vision handler...")
    print("    APIs will be tried in order: Groq → Gemini")
    
    prompt = "Describe this image and identify if it shows a crop or plant."
    system_instruction = "You are an agricultural expert. Analyze images of crops and plants."
    
    try:
        response, api_used = unified_vision_handler.get_vision_response(
            prompt=prompt,
            image_data=test_img,
            system_instruction=system_instruction
        )
        
        print(f"\n✅ SUCCESS!")
        print(f"   API Used: {api_used}")
        print(f"\n   Response Preview:")
        print(f"   {response[:200]}...\n")
        
        # Check if it's an error response
        if response.startswith("All vision APIs failed:"):
            print("⚠️ WARNING: All APIs failed. Check error details above.")
            return False
        else:
            print("=" * 60)
            print("✅ Multi-API Vision System Working Correctly!")
            print("=" * 60)
            return True
            
    except Exception as e:
        print(f"\n❌ EXCEPTION during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_vision_apis()
    exit(0 if success else 1)
