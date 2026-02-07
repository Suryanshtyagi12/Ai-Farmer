import streamlit as st
import streamlit.components.v1 as components
from utils.language_handler import language_handler
from utils.llm_groq_client import groq_client
from utils.llm_gemini_vision_client import gemini_vision_client
from utils.image_handler import image_handler
from utils.rule_based_fallbacks import get_crop_fallback, get_disease_fallback, get_irrigation_fallback
import os
import json

# Page Config
st.set_page_config(page_title="Stable AI Farming Assistant", layout="wide", page_icon="🌾")

# Load Prompt Functions
def load_prompt(filename):
    try:
        with open(f"prompts/{filename}", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

# --- Unified Voice Component ---
# This single component handles the Microphone UI, STT, and TTS.
# It is re-rendered with new arguments (text_to_speak) when needed.
def voice_widget(text_to_speak=None, lang='en'):
    # Escape text for JS
    safe_text = (text_to_speak or "").replace('"', '\\"').replace('\n', ' ').replace("'", "\\'")
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: sans-serif; margin: 0; padding: 0; background: transparent; }}
            .voice-controls {{ display: flex; gap: 10px; flex-direction: column; }}
            .voice-btn {{
                background: linear-gradient(135deg, #2ecc71, #27ae60);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 50px;
                font-size: 16px;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                display: flex;
                align-items: center;
                gap: 8px;
                transition: transform 0.1s;
                width: 100%;
                justify-content: center;
            }}
            .voice-btn:active {{ transform: scale(0.95); }}
            .voice-btn:hover {{ background: linear-gradient(135deg, #27ae60, #219150); }}
            .voice-btn.listening {{ background: linear-gradient(135deg, #e74c3c, #c0392b); animation: pulse 1.5s infinite; }}
            .speak-btn {{ background: linear-gradient(135deg, #3498db, #2980b9); }}
            .speak-btn:hover {{ background: linear-gradient(135deg, #2980b9, #21618c); }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
            .status {{ font-size: 12px; color: #666; margin-top: 4px; text-align: center; }}
            .status.error {{ color: #e74c3c; font-weight: bold; }}
            .status.success {{ color: #27ae60; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="voice-controls">
            <button class="voice-btn" id="voiceBtn" onclick="startListening()">
                <span>🎙️</span> <span id="btn-text">{"Speak Answer" if lang == 'en' else "बोलकर जवाब दें"}</span>
            </button>
            {"<button class='voice-btn speak-btn' id='speakBtn' onclick='speakText()'>🔊 " + ("Hear Question" if lang == 'en' else "सवाल सुनें") + "</button>" if text_to_speak else ""}
        </div>
        <div id="status" class="status"></div>

        <script>
            const LANG = "{'hi-IN' if lang == 'hi' else 'en-US'}";
            const TEXT_TO_SPEAK = "{safe_text}";
            let isListening = false;
            let hasSpoken = false;

            // SPEECH SYNTHESIS (TTS)
            function speakText() {{
                if (!TEXT_TO_SPEAK) return;
                
                const status = document.getElementById('status');
                status.className = 'status';
                status.innerText = "{'🔊 Speaking...' if lang == 'en' else '🔊 बोल रहा हूँ...'}";
                
                // Cancel any ongoing speech
                window.speechSynthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(TEXT_TO_SPEAK);
                utterance.lang = LANG;
                utterance.rate = 0.85; // Slower for better clarity
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                // For Hindi, ensure proper voice selection
                const voices = window.speechSynthesis.getVoices();
                if (LANG === 'hi-IN') {{
                    const hindiVoice = voices.find(v => v.lang.startsWith('hi'));
                    if (hindiVoice) {{
                        utterance.voice = hindiVoice;
                        console.log('Using Hindi voice:', hindiVoice.name);
                    }} else {{
                        console.warn('No Hindi voice found, using default');
                    }}
                }}
                
                utterance.onend = () => {{
                    status.innerText = "";
                    hasSpoken = true;
                }};
                
                utterance.onerror = (e) => {{
                    console.error('TTS Error:', e);
                    status.className = 'status error';
                    status.innerText = "{'Error speaking' if lang == 'en' else 'बोलने में त्रुटि'}";
                }};
                
                window.speechSynthesis.speak(utterance);
            }}

            // Auto-speak ONLY if voices are loaded and user has interacted
            // Browsers block auto-play without user interaction
            if (TEXT_TO_SPEAK && !hasSpoken) {{
                // Wait for voices to load
                function tryAutoSpeak() {{
                    const voices = window.speechSynthesis.getVoices();
                    if (voices.length > 0) {{
                        // Auto-speak on first load (after user navigated to page)
                        setTimeout(() => {{
                            speakText();
                        }}, 800);
                    }} else {{
                        // Voices not loaded yet, wait for event
                        window.speechSynthesis.onvoiceschanged = () => {{
                            setTimeout(() => {{
                                speakText();
                            }}, 800);
                        }};
                    }}
                }}
                
                // Try auto-speak
                tryAutoSpeak();
            }}

            // SPEECH RECOGNITION (STT)
            function startListening() {{
                const status = document.getElementById('status');
                const btn = document.getElementById('voiceBtn');
                const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                
                if (!Recognition) {{
                    status.className = 'status error';
                    status.innerText = "{'Browser does not support voice recognition. Try Chrome or Edge.' if lang == 'en' else 'ब्राउज़र वॉइस को सपोर्ट नहीं करता। Chrome या Edge आज़माएं।'}";
                    return;
                }}

                if (isListening) {{
                    status.innerText = "{'Already listening...' if lang == 'en' else 'पहले से सुन रहा हूँ...'}";
                    return;
                }}

                const recognition = new Recognition();
                recognition.lang = LANG;
                recognition.interimResults = false;
                recognition.maxAlternatives = 1;
                recognition.continuous = false;

                isListening = true;
                btn.classList.add('listening');
                status.className = 'status';
                status.innerText = "{'🎤 Listening... Speak now!' if lang == 'en' else '🎤 सुन रहा हूँ... बोलिए!'}";
                
                try {{
                    recognition.start();
                }} catch (e) {{
                    console.error('Recognition start error:', e);
                    status.className = 'status error';
                    status.innerText = "{'Error starting microphone. Try again.' if lang == 'en' else 'माइक्रोफोन शुरू करने में त्रुटि। फिर कोशिश करें।'}";
                    isListening = false;
                    btn.classList.remove('listening');
                    return;
                }}

                recognition.onresult = (event) => {{
                    const transcript = event.results[0][0].transcript;
                    const confidence = event.results[0][0].confidence;
                    
                    console.log('Recognized:', transcript, 'Confidence:', confidence);
                    
                    status.className = 'status success';
                    status.innerText = `✓ ${{transcript}}`;
                    
                    // Send to Streamlit chat input
                    try {{
                        const input = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                        const submit = window.parent.document.querySelector('button[data-testid="stChatInputSubmitButton"]');
                        
                        if (input && submit) {{
                            // Use native setter to properly trigger React
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                            nativeInputValueSetter.call(input, transcript);
                            
                            // Trigger input event
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            
                            // Submit after short delay
                            setTimeout(() => {{
                                submit.click();
                                status.innerText = "{'✓ Submitted!' if lang == 'en' else '✓ भेज दिया!'}";
                            }}, 300);
                        }} else {{
                            status.className = 'status error';
                            status.innerText = "{'Error: Chat input not found' if lang == 'en' else 'त्रुटि: चैट इनपुट नहीं मिला'}";
                        }}
                    }} catch (e) {{
                        console.error('Injection error:', e);
                        status.className = 'status error';
                        status.innerText = "{'Error submitting text' if lang == 'en' else 'टेक्स्ट भेजने में त्रुटि'}";
                    }}
                }};

                recognition.onerror = (event) => {{
                    console.error('Recognition error:', event.error);
                    status.className = 'status error';
                    
                    let errorMsg = '';
                    if (event.error === 'not-allowed' || event.error === 'permission-denied') {{
                        errorMsg = "{'Microphone blocked. Click 🔒 in address bar → Allow microphone' if lang == 'en' else 'माइक्रोफोन ब्लॉक है। एड्रेस बार में 🔒 क्लिक करें → माइक्रोफोन की अनुमति दें'}";
                    }} else if (event.error === 'no-speech') {{
                        errorMsg = "{'No speech heard. Speak louder or check microphone.' if lang == 'en' else 'कोई आवाज़ नहीं सुनाई दी। ज़ोर से बोलें या माइक जांचें।'}";
                    }} else if (event.error === 'network') {{
                        errorMsg = "{'Network issue. Speech recognition needs internet. Check connection or use text input.' if lang == 'en' else 'नेटवर्क समस्या। वॉइस को इंटरनेट चाहिए। कनेक्शन जांचें या टेक्स्ट इनपुट करें।'}";
                    }} else if (event.error === 'aborted') {{
                        errorMsg = "{'Recognition stopped. Try again.' if lang == 'en' else 'रुक गया। फिर कोशिश करें।'}";
                    }} else {{
                        errorMsg = `Error: ${{event.error}}`;
                    }}
                    
                    status.innerText = "❌ " + errorMsg;
                    isListening = false;
                    btn.classList.remove('listening');
                }};
                
                recognition.onend = () => {{
                    isListening = false;
                    btn.classList.remove('listening');
                    if (status.innerText.includes('Listening') || status.innerText.includes('सुन रहा')) {{
                        status.className = 'status';
                        status.innerText = "{'Click 🎙️ to speak again' if lang == 'en' else 'फिर बोलने के लिए 🎙️ दबाएं'}";
                    }}
                }};
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=120)

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "lang" not in st.session_state: st.session_state.lang = "en"
if "voice_step" not in st.session_state: st.session_state.voice_step = "welcome"
if "data_slots" not in st.session_state: st.session_state.data_slots = {}
if "active_flow" not in st.session_state: st.session_state.active_flow = None
if "last_spoken_hash" not in st.session_state: st.session_state.last_spoken_hash = ""

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
    
    voice_widget("", st.session_state.lang) # Just the button
    
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
                voice_widget(response[:200], st.session_state.lang) # Speak result
        else:
            st.warning("Please enter location.")

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
                voice_widget(response[:200], st.session_state.lang)

# Feature: Smart Farmer Interaction (Sequential Voice Flow)
else:
    # Check if HTTPS (voice will work) or HTTP (voice may not work)
    import streamlit.web.server.server as server
    
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Define all flows including disease
    FLOWS = {
        "crop": ["q_location", "q_season", "q_profit", "q_soil", "q_water"],
        "irrigation": ["q_location", "q_crop", "q_soil", "q_rainfall"],
        "disease": []  # Disease doesn't need sequential questions, just image upload
    }
    
    # Determine current state and what to say
    text_to_announce = None
    current_q = None
    show_voice_widget = True
    
    # STEP 1: Welcome
    if st.session_state.voice_step == "welcome":
        msg = language_handler.get_text("welcome")
        st.info(f"🤖 {msg}")
        text_to_announce = msg
        st.session_state.voice_step = "select_category"
        st.session_state.last_spoken_hash = "welcome"
        
        # Show HTTPS warning for localhost
        if "localhost" in st.context.headers.get("Host", "") or "127.0.0.1" in st.context.headers.get("Host", ""):
            st.warning("⚠️ Voice may not work on localhost (HTTP). For full voice support, deploy to Streamlit Cloud (HTTPS) or use text input below." if st.session_state.lang == "en" 
                      else "⚠️ लोकलहोस्ट पर वॉइस काम नहीं कर सकता। पूर्ण वॉइस के लिए, Streamlit Cloud पर डिप्लॉय करें या नीचे टेक्स्ट इनपुट करें।")
    
    # STEP 2: Ask what they want help with
    elif st.session_state.voice_step == "select_category":
        current_q = "ask_category"
        q_text = language_handler.get_text(current_q)
        st.info(f"🎤 {q_text}")
        
        if st.session_state.last_spoken_hash != current_q:
            text_to_announce = q_text
            st.session_state.last_spoken_hash = current_q
    
    # STEP 3: Gathering data for selected flow
    elif st.session_state.voice_step == "gathering":
        if st.session_state.active_flow == "disease":
            # Special handling for disease - redirect to upload
            st.warning(language_handler.get_text("upload_image") if st.session_state.lang == "en" 
                      else "कृपया साइडबार से 'रोग की जांच' चुनें और फोटो अपलोड करें।")
            show_voice_widget = False
        else:
            steps = FLOWS.get(st.session_state.active_flow, [])
            for step in steps:
                if step not in st.session_state.data_slots:
                    current_q = step
                    break
            
            if current_q:
                q_text = language_handler.get_text(current_q)
                optional_fields = ["q_soil", "q_water"]
                hint = " " + language_handler.get_text("optional_hint") if current_q in optional_fields else ""
                full_q = q_text + hint
                
                st.info(f"🎤 {full_q}")
                
                # Only speak if this is a new question
                if st.session_state.last_spoken_hash != current_q:
                    text_to_announce = full_q
                    st.session_state.last_spoken_hash = current_q
            else:
                # All questions answered, move to finalize
                st.session_state.voice_step = "finalize"
                st.rerun()
    
    # STEP 4: Generate final recommendation
    elif st.session_state.voice_step == "finalize":
        with st.spinner(language_handler.get_text("finishing") if st.session_state.lang == "en" else "विश्लेषण कर रहा हूँ..."):
            # Build detailed prompt based on collected data
            flow_type = st.session_state.active_flow
            data = st.session_state.data_slots
            
            if flow_type == "crop":
                prompt = f"""Provide a brief crop recommendation for:
Location: {data.get('q_location', 'Unknown')}
Season: {data.get('q_season', 'Unknown')}
Profit Priority: {data.get('q_profit', 'Medium')}
Soil Type: {data.get('q_soil', 'Not specified')}
Water Availability: {data.get('q_water', 'Normal')}

Give 2-3 crop suggestions with brief reasons. Keep response under 100 words for voice."""
            
            elif flow_type == "irrigation":
                prompt = f"""Provide brief irrigation advice for:
Location: {data.get('q_location', 'Unknown')}
Crop: {data.get('q_crop', 'Unknown')}
Soil Type: {data.get('q_soil', 'Not specified')}
Rainfall: {data.get('q_rainfall', 'Normal')}

Give practical irrigation schedule and water management tips. Keep under 100 words for voice."""
            
            else:
                prompt = f"Provide farming advice based on: {data}"
            
            sys_instruction = load_prompt("system_prompt.txt") + f"\n\nRESPOND IN {st.session_state.lang.upper()} LANGUAGE. BE CONCISE AND PRACTICAL. MAX 100 WORDS."
            
            response = groq_client.get_completion(prompt, system_instruction=sys_instruction)
            
            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Speak the response
            text_to_announce = response
            st.session_state.voice_step = "done"
            st.session_state.last_spoken_hash = "final_response"
    
    # STEP 5: Done - show completion message
    elif st.session_state.voice_step == "done":
        completion_msg = "Thank you! You can ask another question or reset the chat." if st.session_state.lang == "en" else "धन्यवाद! आप एक और सवाल पूछ सकते हैं या चैट रीसेट कर सकते हैं।"
        st.success(completion_msg)
        
        if st.session_state.last_spoken_hash != "done_message":
            text_to_announce = completion_msg
            st.session_state.last_spoken_hash = "done_message"
        
        # Auto-reset for next question after showing done message
        if st.button("🔄 " + ("Ask Another Question" if st.session_state.lang == "en" else "नया सवाल पूछें")):
            st.session_state.voice_step = "select_category"
            st.session_state.data_slots = {}
            st.session_state.active_flow = None
            st.session_state.last_spoken_hash = ""
            st.rerun()
        
        show_voice_widget = False  # Don't show voice widget on done screen
    
    # RENDER VOICE WIDGET (BEFORE chat input so it's always accessible)
    if show_voice_widget:
        voice_widget(text_to_announce, st.session_state.lang)
    
    # CHAT INPUT for text-based responses (alternative to voice)
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
