import os
import base64
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqVisionClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
    
    def get_vision_completion(self, prompt, image_data, system_instruction=None):
        """
        Get vision completion from Groq's Llama 3.2 Vision model.
        
        Args:
            prompt: Text prompt for the vision task
            image_data: PIL Image object
            system_instruction: Optional system instruction
        
        Returns:
            Response text from the model
        """
        if not self.client:
            return "Error: GROQ_API_KEY not found for vision tasks."
        
        try:
            # Convert PIL Image to base64
            import io
            buffered = io.BytesIO()
            image_data.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Prepare messages
            messages = []
            if system_instruction:
                messages.append({
                    "role": "system",
                    "content": system_instruction
                })
            
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    }
                ]
            })
            
            # Call Groq API with Llava vision model (currently available)
            response = self.client.chat.completions.create(
                model="llava-v1.5-7b-4096-preview",  # Llava 1.5 7B - currently available vision model
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Groq Vision Error: {str(e)}"

groq_vision_client = GroqVisionClient()
