import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        self.text_model = genai.GenerativeModel('gemini-2.0-flash')
        self.vision_model = genai.GenerativeModel('gemini-2.0-flash')

    def get_completion(self, prompt, system_instruction=None):
        try:
            if system_instruction:
                # Combining system instruction with prompt for flash model if needed, 
                # though some models support system_instruction in constructor
                full_prompt = f"{system_instruction}\n\nTask:\n{prompt}"
            else:
                full_prompt = prompt
            
            response = self.text_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    def get_vision_completion(self, prompt, image_data, system_instruction=None):
        try:
            content = [prompt, image_data]
            if system_instruction:
                prompt_with_sys = f"{system_instruction}\n\n{prompt}"
                content[0] = prompt_with_sys
            
            response = self.vision_model.generate_content(content)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

llm_client = GeminiClient()
