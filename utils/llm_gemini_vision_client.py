import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiVisionClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.model = None
        else:
            genai.configure(api_key=api_key)
            # Using Gemini Exp (experimental) - free and supports vision
            self.model = genai.GenerativeModel('gemini-exp-1206')

    def get_vision_completion(self, prompt, image_data, system_instruction=None):
        if not self.model:
            return "Error: GEMINI_API_KEY not found for vision tasks."
        
        try:
            content = [prompt, image_data]
            if system_instruction:
                prompt_with_sys = f"{system_instruction}\n\n{prompt}"
                content[0] = prompt_with_sys
            
            response = self.model.generate_content(content)
            return response.text
        except Exception as e:
            return f"Gemini Vision Error: {str(e)}"

gemini_vision_client = GeminiVisionClient()
