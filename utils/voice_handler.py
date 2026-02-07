from streamlit_mic_recorder import mic_recorder
import streamlit as st

class VoiceHandler:
    @staticmethod
    def record_audio():
        """
        Displays a mic recorder button and returns the audio output to be processed.
        """
        audio = mic_recorder(
            start_prompt="🎤 Start Recording",
            stop_prompt="🛑 Stop Recording",
            key="voice_recorder"
        )
        return audio

    @staticmethod
    def speech_synthesis(text, lang='en'):
        """
        Synthesizes text to speech using gTTS and returns the audio bytes.
        """
        from gtts import gTTS
        import io
        
        # gTTS uses ISO 639-1 language codes (e.g., 'en', 'hi')
        tts_lang = 'hi' if lang == 'hi' else 'en'
        
        try:
            tts = gTTS(text=text, lang=tts_lang)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            return fp.getvalue()
        except Exception as e:
            st.error(f"TTS Error: {e}")
            return None

voice_handler = VoiceHandler()
