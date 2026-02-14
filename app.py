import streamlit as st
from utils.language_handler import language_handler
from utils.llm_groq_client import groq_client
from utils.unified_vision_handler import unified_vision_handler
from utils.image_handler import image_handler
from utils.rule_based_fallbacks import get_crop_fallback, get_disease_fallback, get_irrigation_fallback
from utils.voice_input_widget import voice_input_widget
from utils.data_handler import get_farmer_data, save_farmer_data, clear_farmer_data
from utils.tracking_logic import calculate_crop_age, get_crop_stage, get_mock_weather
from datetime import datetime, date
from gtts import gTTS
import os
import io
import base64

import re

# ... existing code ...

# Page Config
st.set_page_config(page_title="AI Farming Assistant", layout="wide", page_icon="🌾")

# Load Prompt Functions
def load_prompt(filename):
    try:
        with open(f"prompts/{filename}", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def clean_text_for_tts(text):
    """Clean text for better speech synthesis."""
    if not text: return ""
    # Remove markdown formatting
    text = re.sub(r'[*_#`]', '', text) 
    text = text.replace('•', '')
    text = text.replace('-', '') 
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Auto-play Audio Function using gTTS
def auto_play_audio(text, lang='en'):
    """
    Convert text to speech and auto-play using gTTS
    Works reliably on all platforms
    """
    if not text or len(text.strip()) == 0:
        return
        
    # CLEANUP before TTS
    text = clean_text_for_tts(text)
    
    try:
        # Create TTS
        lang_code = 'hi' if lang == 'hi' else 'en'
        # Use 'co.in' TLD for better connectivity in India
        tts = gTTS(text=text, lang=lang_code, tld='co.in', slow=False)
        
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
        # Graceful error handling - don't crash the UI
        st.toast(f"Voice unavailable: Network error", icon="🔇")
        # st.error(f"Audio Error: {e}") # Debugging only

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
            "Track Farming",
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
        # Soil Type Validation & Selection
        soil_type = st.selectbox(language_handler.get_text("soil"), 
                                 ["Select Soil Type...", "Clay", "Sandy", "Loamy", "Black", "Red", "Unknown"])
        
        n = st.number_input(language_handler.get_text("nitrogen"), min_value=0, value=0)
        p = st.number_input(language_handler.get_text("phosphorus"), min_value=0, value=0)
        k = st.number_input(language_handler.get_text("potassium"), min_value=0, value=0)
    
    if st.button(language_handler.get_text("get_recommendation")):
        # 1. Location Validation
        if not location or len(location) < 3 or location.isdigit():
             st.error("The entered location does not exist. Please check the state or city name.")
             st.stop() # Stop processing
             
        # 2. Input Assembly & Fail-safe
        final_soil = soil_type if soil_type != "Select Soil Type..." else "Typical soil for this region"
        final_water = f"N:{n}, P:{p}, K:{k}" if (n+p+k) > 0 else "Standard NPK assumptions"
        
        with st.spinner("Analyzing soil & climate data..."):
            try:
                # 3. LLM Call
                prompt = load_prompt("crop_prompt.txt").format(
                    location=location, season=season, priority=priority,
                    soil_type=final_soil,
                    water=final_water
                )
                sys = load_prompt("system_prompt.txt") + f"\nRESPOND IN {st.session_state.lang} LANGUAGE."
                response = groq_client.get_completion(prompt, system_instruction=sys)
                
                # 4. Text-Only Output
                st.markdown(response)
                
                # Voice DISABLED by default for this feature as per rules
                # auto_play_audio(response[:300], st.session_state.lang) 
                
            except Exception as e:
                st.error(f"Error: {e}")

# Feature: Irrigation Planning
elif mode == language_handler.get_text("irrigation"):
    st.subheader("🌊 " + language_handler.get_text("irrigation"))
    
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input(language_handler.get_text("location"), placeholder="e.g., Punjab, Maharashtra")
        crop = st.text_input(language_handler.get_text("crop"), placeholder="e.g., Wheat, Rice, Cotton")
        
        # 3. Method Selection
        method = st.radio("Preferred Irrigation Method", ["Drip", "Sprinkler", "Flood", "Not Sure"], horizontal=True)
        
    with col2:
        # Soil Type Validation & Selection
        soil_type = st.selectbox(language_handler.get_text("soil"), 
                                 ["Select Soil Type...", "Clay", "Sandy", "Loamy", "Black", "Red", "Alluvial", "Unknown"])
        
        rainfall = st.selectbox(
            "Rainfall Pattern" if st.session_state.lang == "en" else "वर्षा पैटर्न",
            ["Low (< 500mm)", "Medium (500-1000mm)", "High (> 1000mm)"]
        )
    
    if st.button(language_handler.get_text("get_irrigation")):
        # 2. Input Validation
        if not location or len(location) < 3 or location.isdigit():
             st.error("Please provide a valid state/location name.")
             st.stop()
        
        if not crop or len(crop) < 2:
             st.error("Please provide a valid crop name.")
             st.stop()
             
        # Fail-safe defaults
        final_soil = soil_type if soil_type != "Select Soil Type..." else "Typical soil"
        
        with st.spinner("Generating Irrigation Plan..." if st.session_state.lang == "en" else "सिंचाई योजना तैयार हो रही है..."):
            try:
                sys = load_prompt("system_prompt.txt") + f"\nRESPOND IN {st.session_state.lang}"
                prompt = load_prompt("irrigation_prompt.txt").format(
                    location=location,
                    crop=crop,
                    soil_type=final_soil,
                    water=rainfall
                )
                # Append user method preference if specified
                if method != "Not Sure":
                    prompt += f"\nUser Query: Is {method} irrigation suitable?"
                    
                response = groq_client.get_completion(prompt, system_instruction=sys)
                st.success(response)
                
                # 1. Voice DISABLED by default
                # auto_play_audio(response[:300], st.session_state.lang)
                
            except Exception as e:
                # Fixed Fallback Call
                fallback = get_irrigation_fallback(crop, final_soil, location)
                st.warning(fallback)
                # auto_play_audio(fallback, st.session_state.lang)

# Feature: Disease Check
elif mode == language_handler.get_text("disease"):
    uploaded_file = st.file_uploader(language_handler.get_text("upload_image"), type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = image_handler.process_image(uploaded_file)
        st.image(image, caption="Crop Image", use_container_width=True)
        if st.button("🔍 Analyze Crop Disease"):
            with st.spinner("Analyzing with AI (trying multiple models)..."):
                sys = load_prompt("system_prompt.txt") + f"\nRESPOND IN {st.session_state.lang}"
                response, api_used = unified_vision_handler.get_vision_response(
                    load_prompt("disease_prompt.txt").format(crop_name="Unknown"),
                    image, system_instruction=sys
                )
                st.success(f"✅ Analysis complete (API: {api_used})")
                st.markdown(response)
                # Auto-play audio response
                auto_play_audio(response[:300], st.session_state.lang)

# Feature: Track Farming
elif mode == "Track Farming":
    st.subheader("📋 " + ("Track Your Farm Progress" if st.session_state.lang == "en" else "अपनी खेती की प्रगति ट्रैक करें"))
    
    # Session State for Farmer ID
    if "farmer_id" not in st.session_state:
        st.session_state.farmer_id = None
        
    # --- LOGIN / REGISTER VIEW ---
    if not st.session_state.farmer_id:
        st.info("Please Login to access your farm data." if st.session_state.lang == "en" else "अपने खेती डेटा तक पहुंचने के लिए कृपया लॉगिन करें।")
        
        with st.form("login_form"):
            f_name = st.text_input("Farmer Name" if st.session_state.lang == "en" else "किसान का नाम")
            f_id = st.text_input("Farmer ID (4 Digits)" if st.session_state.lang == "en" else "किसान आईडी (4 अंक)", max_chars=4)
            
            submitted = st.form_submit_button("Login / Register" if st.session_state.lang == "en" else "लॉगिन / रजिस्टर")
            
            if submitted:
                if len(f_id) == 4 and f_id.isdigit() and f_name:
                    st.session_state.farmer_id = f_id
                    st.session_state.farmer_name = f_name
                    st.success(f"Welcome {f_name}!" if st.session_state.lang == "en" else f"स्वागत है {f_name}!")
                    st.rerun()
                else:
                    st.error("Please enter valid Name and 4-digit ID." if st.session_state.lang == "en" else "कृपया सही नाम और 4-अंकों की आईडी दर्ज करें।")
    
    else:
        # --- LOGGED IN VIEW ---
        # Load specific farmer data
        farmer_data = get_farmer_data(st.session_state.farmer_id)
        
        if st.button("Logout" if st.session_state.lang == "en" else "लॉग आउट"):
            st.session_state.farmer_id = None
            st.rerun()
            
        if farmer_data:
            # --- DASHBOARD VIEW ---
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.success(f"Tracking: **{farmer_data['crop_name']}** at **{farmer_data['location']}**")
                
                # Recalculate Stage
                p_date_str = farmer_data['plantation_date']
                
                age_days = calculate_crop_age(p_date_str)
                current_stage = get_crop_stage(farmer_data['crop_name'], age_days)
                
                # Timeline UI
                st.progress(min(100, int((age_days / 150) * 100)))
                st.caption(f"Day {age_days}: **{current_stage}** Phase")
                
                st.info(f"📅 Planted on: {p_date_str}")
                
                # Weather
                weather = get_mock_weather(farmer_data['location'])
                st.metric("Current Weather", f"{weather['temp']}, {weather['condition']}")
                
            with col2:
                st.write("### Actions")
                if st.button("Generate Today's Advisory" if st.session_state.lang == "en" else "आज की सलाह प्राप्त करें"):
                    with st.spinner("Analyzing Farm Status..."):
                        try:
                            # Strict Language Instruction
                            lang_instruction = "Respond ONLY in HINDI." if st.session_state.lang == 'hi' else "Respond ONLY in ENGLISH."
                            sys_instruction = load_prompt("system_prompt.txt") + f"\n{lang_instruction}"
                            
                            prompt = load_prompt("tracking_prompt.txt").format(
                                crop_name=farmer_data['crop_name'],
                                plantation_date=p_date_str,
                                age=age_days,
                                stage=current_stage,
                                location=farmer_data['location'],
                                soil_type=farmer_data['soil_type'],
                                fertilizer=farmer_data['fertilizer'],
                                weather=f"{weather['temp']}, {weather['condition']}, {weather['forecast']}"
                            )
                            advisory = groq_client.get_completion(prompt, system_instruction=sys_instruction)
                            st.markdown(advisory)
                            auto_play_audio(advisory[:400], st.session_state.lang)
                        except Exception as e:
                            st.error(f"Error: {e}")
                
                st.divider()
                if st.button("❌ Stop Tracking" if st.session_state.lang == "en" else "❌ ट्रैकिंग बंद करें"):
                    clear_farmer_data(st.session_state.farmer_id)
                    st.rerun()
                    
        else:
            # --- REGISTRATION VIEW (No data for this ID yet) ---
            st.info("Start tracking your crop cycle for personalized daily tips." if st.session_state.lang == "en" else "दैनिक सुझावों के लिए अपनी फसल चक्र को ट्रैक करना शुरू करें।")
            
            with st.form("track_form"):
                c_name = st.text_input("Crop Name" if st.session_state.lang == "en" else "फसल का नाम", placeholder="Wheat, Rice...")
                c_loc = st.text_input("Farm Location" if st.session_state.lang == "en" else "खेत का स्थान", placeholder="City, District")
                c_soil = st.selectbox("Soil Type" if st.session_state.lang == "en" else "मिट्टी का प्रकार", ["Clay", "Sandy", "Loamy", "Black", "Red"])
                c_fert = st.selectbox("Fertilizer Used" if st.session_state.lang == "en" else "काद/उर्वरक", ["Urea", "DAP", "Organic", "Mixed", "Not Sure"])
                c_date = st.date_input("Date of Plantation" if st.session_state.lang == "en" else "रोपण की तारीख", max_value=date.today())
                
                submitted = st.form_submit_button("Start Tracking" if st.session_state.lang == "en" else "ट्रैकिंग शुरू करें")
                
                if submitted:
                    if c_name and c_loc:
                        new_data = {
                            "crop_name": c_name,
                            "location": c_loc,
                            "soil_type": c_soil,
                            "fertilizer": c_fert,
                            "plantation_date": str(c_date)
                        }
                        # Save with Farmer ID
                        save_farmer_data(st.session_state.farmer_id, new_data)
                        st.success("Tracking Started! Refreshing..." if st.session_state.lang == "en" else "ट्रैकिंग शुरू हो गई! रिफ्रेश हो रहा है...")
                        st.rerun()
                    else:
                        st.error("Please fill Name and Location." if st.session_state.lang == "en" else "कृपया नाम और स्थान भरें।")

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
    
    # QUESTION OPTIONS (Bilingual)
    QUESTION_OPTIONS = {
        "q_season": {
            "en": ["Kharif", "Rabi", "Zaid"],
            "hi": ["खरीफ", "रबी", "जायद"]
        },
        "q_profit": {
            "en": ["Low", "Medium", "High"],
            "hi": ["कम", "मध्यम", "अधिक"]
        },
        "q_soil": {
            "en": ["Clay", "Sandy", "Loamy", "Black", "Red", "Not sure"],
            "hi": ["चिकनी", "रेतीली", "दोमट", "काली", "लाल", "पता नहीं"]
        },
        "q_water": {
             "en": ["Low", "Medium", "High", "Not sure"],
             "hi": ["कम", "मध्यम", "अधिक", "पता नहीं"]
        },
        "q_rainfall": {
             "en": ["Low", "Medium", "High"],
             "hi": ["कम", "मध्यम", "अधिक"]
        }
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
            
        # Category Buttons
        cols = st.columns(3)
        cats = [("Crop Suggestion", "फसल सुझाव"), ("Irrigation", "सिंचाई"), ("Disease", "रोग")]
        for i, (eng, hi) in enumerate(cats):
            label = eng if st.session_state.lang == "en" else hi
            if cols[i].button(label, key=f"cat_{i}"):
                st.session_state.temp_input = eng # Use English key for logic
                st.rerun()
    
    # STEP 3: Gathering data
    elif st.session_state.voice_step == "gathering":
        flow = st.session_state.active_flow
        
        if flow == "disease":
            st.info("📸 " + ("Upload crop image" if st.session_state.lang == "en" else "फसल की तस्वीर अपलोड करें"))
            
            uploaded_file = st.file_uploader("Image" if st.session_state.lang == "en" else "तस्वीर", type=["jpg", "jpeg", "png"])
            
            if uploaded_file:
                img = image_handler.process_image(uploaded_file)
                st.image(img, use_column_width=True)
                
                if st.button("🔍 Analyze" if st.session_state.lang == "en" else "🔍 विश्लेषण"):
                    with st.spinner("Analyzing..." if st.session_state.lang == "en" else "विश्लेषण..."):
                        try:
                            sys = load_prompt("system_prompt.txt") + f"\nRESPOND IN {st.session_state.lang}"
                            result, api_used = unified_vision_handler.get_vision_response(
                                load_prompt("disease_prompt.txt").format(crop_name="Unknown"),
                                img, system_instruction=sys
                            )
                            st.session_state.messages.append({"role": "assistant", "content": result})
                            st.success(f"✅ {result}\n\n_(API: {api_used})_")
                            auto_play_audio(result[:300], st.session_state.lang)
                        except Exception as e:
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
                
                # Check for options
                options = QUESTION_OPTIONS.get(current_q, {}).get(st.session_state.lang, [])
                
                question_hash = f"{flow}_{current_q}_{st.session_state.lang}"
                if question_hash not in st.session_state.audio_played:
                    # Construct spoken text with options
                    spoken_text = question_text
                    if options:
                        opts_str = ", ".join(options)
                        spoken_text += ". " + ("Options are: " if st.session_state.lang == 'en' else "विकल्प हैं: ") + opts_str
                    
                    st.info(f"🤖 {question_text}")
                    auto_play_audio(spoken_text, st.session_state.lang)
                    st.session_state.audio_played.add(question_hash)
                else:
                    st.info(f"🤖 {question_text}")
                
                # Display Options Buttons
                if options:
                    st.write("Options:" if st.session_state.lang == 'en' else "विकल्प:")
                    cols = st.columns(3)
                    for i, opt in enumerate(options):
                        if cols[i % 3].button(opt, key=f"btn_{current_q}_{i}"):
                            st.session_state.temp_input = opt
                            st.rerun()
                            
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
                    data = st.session_state.data_slots
                    prompt = load_prompt("crop_prompt.txt").format(
                        location=data.get('q_location', 'Unknown'),
                        season=data.get('q_season', 'Unknown'),
                        priority=data.get('q_profit', 'Medium'),
                        soil_type=data.get('q_soil', 'Not specified'),
                        water=data.get('q_water', 'Normal')
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
                    result = "An unexpected flow occurred."
                
                st.session_state.messages.append({"role": "assistant", "content": result})
                st.success(result)
                auto_play_audio(result[:500], st.session_state.lang)
            except Exception as e:
                st.error(f"Error during generation: {e}")
                
                # Safe Fallback Logic
                if flow == "crop":
                    fallback = get_crop_fallback(
                        st.session_state.data_slots.get('q_location', 'Unknown'), 
                        st.session_state.data_slots.get('q_season', 'Unknown'),
                        lang=st.session_state.lang
                    )
                elif flow == "irrigation":
                    fallback = get_irrigation_fallback(
                        st.session_state.data_slots.get('q_crop', 'Unknown Crop'),
                        st.session_state.data_slots.get('q_soil', 'Unknown Soil'),
                        st.session_state.data_slots.get('q_location', 'Unknown Location'),
                        lang=st.session_state.lang
                    )
                else:
                    fallback = "I am unable to provide a response at this time." if st.session_state.lang == 'en' else "मैं अभी जवाब देने में असमर्थ हूँ।"
                    
                st.session_state.messages.append({"role": "assistant", "content": fallback})
                st.warning(fallback)
                auto_play_audio(fallback, st.session_state.lang)
        
        st.session_state.voice_step = "done"
        # Don't rerun immediately - let audio play and let user see the result
    
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
    
    # Handle button clicks from temp_input
    if "temp_input" in st.session_state and st.session_state.temp_input:
        user_input = st.session_state.temp_input
        st.session_state.temp_input = None # Clear it
    
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
            elif any(word in choice for word in ["irrigat", "pani", "सिंचाई", "पानी", "sinchai"]):
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
            is_skip = any(word in user_input.lower() for word in ["next", "skip", "अगला", "छोड़", "nahi", "नहीं", "not sure", "pata nahi"])
            
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
