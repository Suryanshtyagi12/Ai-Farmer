import streamlit.components.v1 as components

def voice_input_widget(lang='en'):
    """
    Simple voice input widget with microphone button
    Injects recognized text into Streamlit chat input
    """
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ margin: 0; padding: 10px; background: transparent; font-family: sans-serif; }}
            .mic-btn {{
                background: linear-gradient(135deg, #e74c3c, #c0392b);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 50px;
                font-size: 16px;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.2s;
            }}
            .mic-btn:hover {{ transform: scale(1.05); }}
            .mic-btn:active {{ transform: scale(0.95); }}
            .mic-btn.listening {{
                background: linear-gradient(135deg, #27ae60, #229954);
                animation: pulse 1.5s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
            .status {{ margin-top: 8px; font-size: 13px; color: #555; text-align: center; }}
            .status.error {{ color: #e74c3c; font-weight: bold; }}
            .status.success {{ color: #27ae60; font-weight: bold; }}
        </style>
    </head>
    <body>
        <button class="mic-btn" id="micBtn" onclick="startListening()">
            <span id="icon">🎙️</span>
            <span id="text">{"Speak" if lang == 'en' else "बोलें"}</span>
        </button>
        <div id="status" class="status"></div>

        <script>
            const LANG = "{'hi-IN' if lang == 'hi' else 'en-US'}";
            let isListening = false;

            function startListening() {{
                const btn = document.getElementById('micBtn');
                const status = document.getElementById('status');
                const icon = document.getElementById('icon');
                const text = document.getElementById('text');
                
                const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                
                if (!Recognition) {{
                    status.className = 'status error';
                    status.innerText = "{'Voice not supported. Use Chrome/Edge.' if lang == 'en' else 'वॉइस सपोर्ट नहीं है। Chrome/Edge इस्तेमाल करें।'}";
                    return;
                }}

                if (isListening) return;

                const recognition = new Recognition();
                recognition.lang = LANG;
                recognition.interimResults = false;
                recognition.maxAlternatives = 1;

                isListening = true;
                btn.classList.add('listening');
                icon.innerText = '🎤';
                text.innerText = "{'Listening...' if lang == 'en' else 'सुन रहा हूँ...'}";
                status.className = 'status';
                status.innerText = "{'Speak now!' if lang == 'en' else 'अब बोलें!'}";
                
                recognition.start();

                recognition.onresult = (event) => {{
                    const transcript = event.results[0][0].transcript;
                    
                    status.className = 'status success';
                    status.innerText = `✓ ${{transcript}}`;
                    
                    // Inject into Streamlit chat input
                    try {{
                        const input = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                        const submit = window.parent.document.querySelector('button[data-testid="stChatInputSubmitButton"]');
                        
                        if (input && submit) {{
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                            nativeInputValueSetter.call(input, transcript);
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            
                            setTimeout(() => {{
                                submit.click();
                                status.innerText = "{'✓ Sent!' if lang == 'en' else '✓ भेज दिया!'}";
                            }}, 300);
                        }} else {{
                            status.className = 'status error';
                            status.innerText = "{'Error: Chat input not found' if lang == 'en' else 'त्रुटि: चैट इनपुट नहीं मिला'}";
                        }}
                    }} catch (e) {{
                        status.className = 'status error';
                        status.innerText = "{'Error submitting' if lang == 'en' else 'भेजने में त्रुटि'}";
                    }}
                }};

                recognition.onerror = (event) => {{
                    status.className = 'status error';
                    
                    if (event.error === 'not-allowed' || event.error === 'permission-denied') {{
                        status.innerText = "{'🔒 Microphone blocked. Allow in browser settings.' if lang == 'en' else '🔒 माइक ब्लॉक है। ब्राउज़र सेटिंग में अनुमति दें।'}";
                    }} else if (event.error === 'no-speech') {{
                        status.innerText = "{'No speech detected. Try again.' if lang == 'en' else 'कोई आवाज़ नहीं। फिर कोशिश करें।'}";
                    }} else if (event.error === 'network') {{
                        status.innerText = "{'Network error. Check internet or use text input.' if lang == 'en' else 'नेटवर्क त्रुटि। इंटरनेट जांचें या टेक्स्ट इनपुट करें।'}";
                    }} else {{
                        status.innerText = `Error: ${{event.error}}`;
                    }}
                }};
                
                recognition.onend = () => {{
                    isListening = false;
                    btn.classList.remove('listening');
                    icon.innerText = '🎙️';
                    text.innerText = "{'Speak' if lang == 'en' else 'बोलें'}";
                }};
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=90)
