"""
HuggingFace Vision Client using Free Inference API
Uses BLIP image captioning model - completely free, no API key needed
"""

import requests
from PIL import Image
import io
import base64

class HuggingFaceVisionClient:
    def __init__(self):
        # Using BLIP image captioning - free and works without auth
        self.api_url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    
    def get_vision_completion(self, prompt, image_data, system_instruction=None):
        """
        Get vision completion from HuggingFace BLIP model.
        
        Args:
            prompt: Text prompt for the vision task (used as context)
            image_data: PIL Image object
            system_instruction: Optional (ignored for this model)
        
        Returns:
            Response text from the model
        """
        try:
            # Convert PIL Image to bytes
            buffered = io.BytesIO()
            image_data.save(buffered, format="JPEG")
            image_bytes = buffered.getvalue()
            
            # Call HuggingFace Inference API (FREE - no key needed)
            response = requests.post(
                self.api_url,
                headers={"Content-Type": "application/octet-stream"},
                data=image_bytes,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # BLIP returns: [{"generated_text": "..."}]
                if isinstance(result, list) and len(result) > 0:
                    caption = result[0].get('generated_text', 'Unable to analyze image')
                    # Enhance caption with prompt context
                    return f"Image Analysis: {caption}\\n\\nBased on your question '{prompt}': The image shows {caption.lower()}. For disease detection, please look for spots, discoloration, wilting, or other abnormal features."
                else:
                    return str(result)
            elif response.status_code == 503:
                return f"Model Loading: The model is currently loading (this is normal for free tier). Please try again in 20 seconds."
            else:
                return f"HuggingFace Error: Status {response.status_code}. The free API might be temporarily unavailable. Details: {response.text[:200]}"
                
        except requests.exceptions.Timeout:
            return "Request Timeout: The free inference API is busy. Please try again."
        except Exception as e:
            return f"Vision Analysis Error: {str(e)}"

huggingface_vision_client = HuggingFaceVisionClient()
