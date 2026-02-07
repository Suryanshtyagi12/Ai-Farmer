"""
Simple audio recorder component for Streamlit
Uses streamlit-audio-recorder for easy recording
"""

import streamlit as st
from audio_recorder_streamlit import audio_recorder

def record_audio_widget(lang='en'):
    """
    Display audio recorder widget
    
    Args:
        lang: Language code ('en' or 'hi')
    
    Returns:
        bytes: Recorded audio data or None
    """
    
    label = "🎙️ Click to Record" if lang == 'en' else "🎙️ रिकॉर्ड करने के लिए क्लिक करें"
    
    st.markdown(f"**{label}**")
    
    # Audio recorder returns bytes when recording is done
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e74c3c",
        neutral_color="#2ecc71",
        icon_size="2x",
        pause_threshold=2.0,  # Auto-stop after 2 seconds of silence
    )
    
    return audio_bytes
