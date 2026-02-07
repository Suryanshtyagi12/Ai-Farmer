"""
Voice API Handler using Groq Whisper (STT) and gTTS (TTS)
Free and reliable alternative to browser Web Speech API
"""

import os
import io
import base64
from gtts import gTTS
from groq import Groq

class VoiceAPIHandler:
    def __init__(self):
        """Initialize with Groq client for Whisper"""
        api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key) if api_key else None
    
    def transcribe_audio(self, audio_file, language='en'):
        """
        Transcribe audio using Groq Whisper
        
        Args:
            audio_file: Audio file object (bytes or file-like)
            language: 'en' or 'hi'
        
        Returns:
            str: Transcribed text
        """
        if not self.client:
            return "Error: GROQ_API_KEY not found"
        
        try:
            # Groq Whisper supports multiple languages
            lang_code = 'hi' if language == 'hi' else 'en'
            
            transcription = self.client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                language=lang_code,
                response_format="text"
            )
            
            return transcription
        except Exception as e:
            return f"Transcription Error: {str(e)}"
    
    def text_to_speech(self, text, language='en'):
        """
        Convert text to speech using gTTS (Google Text-to-Speech)
        Free and reliable for both English and Hindi
        
        Args:
            text: Text to convert
            language: 'en' or 'hi'
        
        Returns:
            bytes: Audio data in MP3 format
        """
        try:
            lang_code = 'hi' if language == 'hi' else 'en'
            
            # Create TTS object
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Save to bytes
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            return audio_fp.read()
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    def get_audio_base64(self, audio_bytes):
        """Convert audio bytes to base64 for embedding in HTML"""
        if audio_bytes:
            return base64.b64encode(audio_bytes).decode()
        return None

# Global instance
voice_api_handler = VoiceAPIHandler()
