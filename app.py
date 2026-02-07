import streamlit as st
from utils.language_handler import language_handler
from utils.llm_groq_client import groq_client
from utils.llm_gemini_vision_client import gemini_vision_client
from utils.image_handler import image_handler
from utils.rule_based_fallbacks import get_crop_fallback, get_disease_fallback, get_irrigation_fallback
from utils.voice_input_widget import voice_input_widget
from gtts import gTTS
import os
import io
import base64

# Page Config
st.set_page_config(page_title="AI Farming Assistant", layout="wide", page_icon="🌾")

# Load Prompt Functions
def load_prompt(filename):
    try:
        with open(f"prompts/{filename}", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

# Auto-play Audio Function using gTTS
def auto_play_audio(text, lang='en'):
    """
    Convert text to speech and auto-play using gTTS
    Works reliably on all platforms
    """
    if not text or len(text.strip()) == 0:
        return
    
    try:
        # Create TTS
        lang_code = 'hi' if lang == 'hi' else 'en'
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Save to bytes
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        # Convert to base64 for HTML audio
        audio_bytes = audio_fp.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # Auto-play using HTML audio with autoplay
        audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Audio Error: {e}")

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "lang" not in st.session_state: st.session_state.lang = "en"
if "voice_step" not in st.session_state: st.session_state.voice_step = "welcome"
if "data_slots" not in st.session_state: st.session_state.data_slots = {}
if "active_flow" not in st.session_state: st.session_state.active_flow = None
if "last_spoken_hash" not in st.session_state: st.session_state.last_spoken_hash = ""
if "audio_played" not in st.session_state: st.session_state.audio_played = set()

# Sidebar
with st.sidebar:
    st.title("🌾 " + language_handler.get_text("title"))
    lang_choice = st.selectbox(
        language_handler.get_text("language_select"),
        options=["English", "हिंदी"],
        index=0 if st.session_state.lang == "en" else 1
    )
    st.session_state.lang = "en" if lang_choice == "English" else "hi"
    language_handler.set_language(st.session_state.lang)
    
    st.divider()
    
    mode = st.radio(
        language_handler.get_text("mode_select"),
        options=[
            language_handler.get_text("crop_rec"),
            language_handler.get_text("irrigation"),
            language_handler.get_text("disease"),
            language_handler.get_text("chat")
        ]
    )
    
    st.divider()
    if st.button("🔄 " + ("Reset Application" if st.session_state.lang == 'en' else "ऐप रीसेट करें")):
        st.session_state.messages = []
        st.session_state.voice_step = "welcome"
        st.session_state.data_slots = {}
        st.session_state.active_flow = None
        st.session_state.last_spoken_hash = ""
        st.session_state.audio_played = set()
        st.rerun()

st.title(mode)

# Feature: Crop Recommendation
if mode == language_handler.get_text("crop_rec"):
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input(language_handler.get_text("location"))
        season = st.selectbox(language_handler.get_text("season"), [
            language_handler.get_text("kharif"),
            language_handler.get_text("rabi"),
            language_handler.get_text("zaid")
        ])
        priority = st.select_slider(language_handler.get_text("profit"), options=[
            language_handler.get_text("low"),
            language_handler.get_text("medium"),
            language_handler.get_text("high")
        ])
    with col2:
        soil_type = st.text_input(language_handler.get_text("soil"))
        n = st.number_input(language_handler.get_text("nitrogen"), min_value=0, value=0)
        p = st.number_input(language_handler.get_text("phosphorus"), min_value=0, value=0)
        k = st.number_input(language_handler.get_text("potassium"), min_value=0, value=0)
    
    if st.button(language_handler.get_text("get_recommendation")):
        if location:
            with st.spinner("Groq Analyzing..."):
                prompt = load_prompt("crop_prompt.txt").format(
                    location=location, season=season, priority=priority,
                    soil_type=soil_type if soil_type else "Not specified",
                    water=f"N:{n}, P:{p}, K:{k}"
                )
                sys = load_prompt("system_prompt.txt") + f"\nRESPOND IN {st.session_state.lang}"
                response = groq_client.get_completion(prompt, system_instruction=sys)
                st.markdown(response)
                # Auto-play audio response
                auto_play_audio(response[:300], st.session_state.lang)
        else:
            st.warning("Please enter location.")

# Feature: Irrigation Planning
elif mode == language_handler.get_text("irrigation"):
    st.subheader("🌊 " + language_handler.get_text("irrigation"))
    
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input(language_handler.get_text("location"), placeholder="e.g., Punjab, Maharashtra")
        crop = st.text_input(language_handler.get_text("crop"), placeholder="e.g., Wheat, Rice, Cotton")
    with col2:
        soil_type = st.selectbox(
            language_handler.get_text("soil"),
            ["Sandy", "Clay", "Loamy", "Black Soil", "Red Soil", "Alluvial"]
        )
        rainfall = st.selectbox(
            "Rainfall Pattern" if st.session_state.lang == "en" else "वर्षा पैटर्न",
            ["Low (< 500mm)", "Medium (500-1000mm)", "High (> 1000mm)"]
        )
    
    if st.button(language_handler.get_text("get_irrigation")):
        if location and crop:
            with st.spinner("Generating Irrigation Plan..." if st.session_state.lang == "en" else "सिंचाई योजना तैयार हो रही है..."):
                try:
                    sys = load_prompt("system_prompt.txt") + f"\nRESPOND IN {st.session_state.lang}"
                    prompt = load_prompt("irrigation_prompt.txt").format(
                        location=location,
                        crop=crop,
                        soil_type=soil_type,
                        water=rainfall
                    )
                    response = groq_client.get_completion(prompt, system_instruction=sys)
                    st.success(response)
                    # Auto-play audio response
                    auto_play_audio(response[:300], st.session_state.lang)
                except:
                    fallback = get_irrigation_fallback()
                    st.warning(fallback)
                    auto_play_audio(fallback, st.session_state.lang)
        else:
            st.error("Please provide location and crop name" if st.session_state.lang == "en" 
                    else "कृपया स्थान और फसल का नाम दें")

# Feature: Disease Check
elif mode == language_handler.get_text("disease"):
    uploaded_file = st.file_uploader(language_handler.get_text("upload_image"), type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = image_handler.process_image(uploaded_file)
        st.image(image, caption="Crop Image", use_container_width=True)
        if st.button("Identify (Gemini)"):
            with st.spinner("Scanning..."):
                sys = load_prompt("system_prompt.txt") + f"\nRESPOND IN {st.session_state.lang}"
                response = gemini_vision_client.get_vision_completion(
                    load_prompt("disease_prompt.txt").format(crop_name="Unknown"),
                    image, system_instruction=sys
                )
                st.markdown(response)
                # Auto-play audio response
                auto_play_audio(response[:300], st.session_state.lang)

# Feature: Smart Talk (Text Input + Auto-Play Audio)
else:
    st.info("💬 " + ("AI will speak responses. Type your answers below." if st.session_state.lang == "en" 
                     else "AI अपने जवाब बोलेगा। नीचे टाइप करें।"))
    
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Define all flows
    FLOWS = {
        "crop": ["q_location", "q_season", "q_profit", "q_soil", "q_water"],
        "irrigation": ["q_location", "q_crop", "q_soil", "q_rainfall"],
        "disease": []
    }
    
    # STEP 1: Welcome
    if st.session_state.voice_step == "welcome":
        msg = language_handler.get_text("welcome")
        st.info(f"🤖 {msg}")
        
        audio_hash = f"welcome_{st.session_state.lang}"
        if audio_hash not in st.session_state.audio_played:
            auto_play_audio(msg, st.session_state.lang)
            st.session_state.audio_played.add(audio_hash)
        
        st.session_state.voice_step = "select_category"
    
    # STEP 2: Category selection
    elif st.session_state.voice_step == "select_category":
        msg = language_handler.get_text("ask_category")
        st.info(f"🤖 {msg}")
        
        audio_hash = f"category_{st.session_state.lang}"
        if audio_hash not in st.session_state.audio_played:
            auto_play_audio(msg, st.session_state.lang)
            st.session_state.audio_played.add(audio_hash)
    
    # STEP 3: Gathering data
    elif st.session_state.voice_step == "gathering":
        flow = st.session_state.active_flow
        
        if flow == "disease":
            st.info("📸 " + ("Upload crop image" if st.session_state.lang == "en" else "फसल की तस्वीर अपलोड करें"))
            
            uploaded_file = st.file_uploader("Image" if st.session_state.lang == "en" else "तस्वीर", type=["jpg", "jpeg", "png"])
            
            if uploaded_file:
                img = image_handler.process_image(uploaded_file) # Changed from load_image to process_image
                st.image(img, use_column_width=True)
                
                if st.button("🔍 Analyze" if st.session_state.lang == "en" else "🔍 विश्लेषण"):
                    with st.spinner("Analyzing..." if st.session_state.lang == "en" else "विश्लेषण..."):
                        try:
                            # Assuming gemini_vision_client is a function that takes prompt and image
                            # The original code had gemini_vision_client.get_vision_completion
                            # Adjusting to match the provided snippet's assumed usage
                            sys = load_prompt("system_prompt.txt") + f"\nRESPOND IN {st.session_state.lang}"
                            result = gemini_vision_client.get_vision_completion(
                                load_prompt("disease_prompt.txt").format(crop_name="Unknown"),
                                img, system_instruction=sys
                            )
                            st.session_state.messages.append({"role": "assistant", "content": result})
                            st.success(result)
                            auto_play_audio(result[:300], st.session_state.lang)
                        except Exception as e: # Added exception handling
                            st.error(f"Error during analysis: {e}")
                            fallback = get_disease_fallback()
                            st.session_state.messages.append({"role": "assistant", "content": fallback})
                            st.warning(fallback)
                            auto_play_audio(fallback, st.session_state.lang)
                    
                    st.session_state.voice_step = "done"
                    st.rerun()
        else:
            questions = FLOWS[flow]
            answered = [q for q in questions if q in st.session_state.data_slots]
            
            if len(answered) < len(questions):
                current_q = questions[len(answered)]
                question_text = language_handler.get_text(current_q)
                
                question_hash = f"{flow}_{current_q}_{st.session_state.lang}"
                if question_hash not in st.session_state.audio_played:
                    st.info(f"🤖 {question_text}")
                    auto_play_audio(question_text, st.session_state.lang)
                    st.session_state.audio_played.add(question_hash)
                else:
                    st.info(f"🤖 {question_text}")
            else:
                st.session_state.voice_step = "finalizing"
                st.rerun()
    
    # STEP 4: Generate recommendation
    elif st.session_state.voice_step == "finalizing":
        flow = st.session_state.active_flow
        
        with st.spinner("Generating..." if st.session_state.lang == "en" else "तैयार हो रहा है..."):
            try:
                sys_instruction = load_prompt("system_prompt.txt") + f"\n\nRESPOND IN {st.session_state.lang.upper()} LANGUAGE. BE CONCISE AND PRACTICAL. MAX 100 WORDS."
                if flow == "crop":
                    # Ensure all slots are present for formatting
                    data = st.session_state.data_slots
                    prompt = load_prompt("crop_prompt.txt").format(
                        location=data.get('q_location', 'Unknown'),
                        season=data.get('q_season', 'Unknown'),
                        priority=data.get('q_profit', 'Medium'),
                        soil_type=data.get('q_soil', 'Not specified'),
                        water=data.get('q_water', 'Normal') # Assuming q_water is a string like "N:10, P:5, K:20" or "Normal"
                    )
                    result = groq_client.get_completion(prompt, system_instruction=sys_instruction)
                elif flow == "irrigation":
                    data = st.session_state.data_slots
                    prompt = load_prompt("irrigation_prompt.txt").format(
                        location=data.get('q_location', 'Unknown'),
                        crop=data.get('q_crop', 'Unknown'),
                        soil=data.get('q_soil', 'Not specified'),
                        rainfall=data.get('q_rainfall', 'Normal')
                    )
                    result = groq_client.get_completion(prompt, system_instruction=sys_instruction)
                else:
                    result = "An unexpected flow occurred." # Fallback for unknown flow
                
                st.session_state.messages.append({"role": "assistant", "content": result})
                st.success(result)
                auto_play_audio(result[:500], st.session_state.lang)
            except Exception as e: # Added exception handling
                st.error(f"Error during generation: {e}")
                fallback = get_crop_fallback() if flow == "crop" else get_irrigation_fallback()
                st.session_state.messages.append({"role": "assistant", "content": fallback})
                st.warning(fallback)
                auto_play_audio(fallback, st.session_state.lang)
        
        st.session_state.voice_step = "done"
        st.rerun()
    
    # STEP 5: Done
    elif st.session_state.voice_step == "done":
        msg = language_handler.get_text("done_message")
        st.success(f"✅ {msg}")
        
        audio_hash = f"done_{st.session_state.lang}"
        if audio_hash not in st.session_state.audio_played:
            auto_play_audio(msg, st.session_state.lang)
            st.session_state.audio_played.add(audio_hash)
        
        if st.button("🔄 " + ("New Question" if st.session_state.lang == "en" else "नया सवाल")):
            st.session_state.voice_step = "select_category"
            st.session_state.data_slots = {}
            st.session_state.active_flow = None
            st.session_state.audio_played = set()
            st.rerun()
    
    # VOICE INPUT WIDGET (Microphone button for voice input)
    st.markdown("---")
    voice_input_widget(st.session_state.lang)
    
    # TEXT INPUT for user responses
    user_input = st.chat_input(language_handler.get_text("input_placeholder"))
    
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Process based on current step
        if st.session_state.voice_step == "select_category":
            choice = user_input.lower()
            
            # Detect intent
            if any(word in choice for word in ["crop", "fasal", "फसल", "खेती"]):
                st.session_state.active_flow = "crop"
                st.session_state.voice_step = "gathering"
            elif any(word in choice for word in ["irrigat", "pani", "सिंचाई", "पानी"]):
                st.session_state.active_flow = "irrigation"
                st.session_state.voice_step = "gathering"
            elif any(word in choice for word in ["disease", "dis", "rog", "रोग", "बीमारी"]):
                st.session_state.active_flow = "disease"
                st.session_state.voice_step = "gathering"
            else:
                # Couldn't detect, ask again
                st.warning("Please specify: Crop, Irrigation, or Disease" if st.session_state.lang == "en" 
                          else "कृपया बताएं: फसल, सिंचाई, या रोग")
            
            st.session_state.last_spoken_hash = ""  # Reset to speak next question
        
        elif st.session_state.voice_step == "gathering" and current_q:
            # Check if user wants to skip
            is_skip = any(word in user_input.lower() for word in ["next", "skip", "अगला", "छोड़", "nahi", "नहीं"])
            
            # Store the answer
            st.session_state.data_slots[current_q] = "Not specified" if is_skip else user_input
            
            # Reset hash so next question will be spoken
            st.session_state.last_spoken_hash = ""
        
        elif st.session_state.voice_step == "done":
            # User wants to continue conversation
            st.session_state.voice_step = "select_category"
            st.session_state.data_slots = {}
            st.session_state.active_flow = None
            st.session_state.last_spoken_hash = ""
        
        # Rerun to show next question
        st.rerun()

st.markdown("---")
st.caption("Farming Assistant Demo | Groq + Gemini + Native Voice")
