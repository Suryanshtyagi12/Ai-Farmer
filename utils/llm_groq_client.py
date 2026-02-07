import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            # Placeholder/Safe behavior if key is missing during first setup
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"

    def get_completion(self, prompt, system_instruction=None):
        if not self.client:
            return "Error: GROQ_API_KEY not found. Please add it to your .env file."
        
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Groq Error: {str(e)}"

groq_client = GroqClient()
