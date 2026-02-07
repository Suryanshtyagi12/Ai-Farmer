# 🌾 AI Farming Assistant

A voice-first AI farming assistant for Indian farmers, supporting both **English** and **Hindi** languages. Get crop recommendations, irrigation advice, and disease detection through natural voice conversations.

## ✨ Features

- 🎙️ **Voice-First Interface**: Complete voice interaction in English and Hindi
- 🌱 **Crop Recommendations**: Get personalized crop suggestions based on location, season, and soil
- 💧 **Irrigation Advice**: Smart water management recommendations
- 🦠 **Disease Detection**: AI-powered crop disease identification from images
- 🌐 **Bilingual Support**: Seamless switching between English and Hindi
- 🤖 **Dual AI Backend**: Groq for text, Gemini Vision for images

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API Keys:
  - Groq API Key ([Get it here](https://console.groq.com))
  - Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Suryanshtyagi12/Ai-Farmer.git
cd Ai-Farmer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Run the app:
```bash
streamlit run app.py
```

## 🎯 Usage

### Smart Talk Mode (Voice-First)
1. Select language (English/हिंदी)
2. Choose "Smart Talk" / "स्मार्ट बातचीत"
3. Click 🎙️ to speak or use text input
4. Follow the AI's sequential questions
5. Get personalized recommendations

### Direct Modes
- **Crop Recommendation**: Fill form with location, season, soil details
- **Disease Detection**: Upload crop image for AI analysis
- **Irrigation Advice**: Get water management tips

## ⚠️ Important Notes

### Voice Features
- **Auto-Speak (TTS)**: Works everywhere ✅
- **Voice Input (STT)**: Requires HTTPS (works on Streamlit Cloud, not localhost) ⚠️

### For Full Voice Support:
Deploy to **Streamlit Cloud** or any HTTPS hosting platform. Voice recognition requires secure connection.

## 🏗️ Architecture

```
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                       # API keys (create this)
├── prompts/                   # AI prompt templates
│   ├── system_prompt.txt
│   ├── crop_prompt.txt
│   ├── irrigation_prompt.txt
│   └── disease_prompt.txt
└── utils/
    ├── language_handler.py    # Bilingual text management
    ├── llm_groq_client.py     # Groq API client
    ├── llm_gemini_vision_client.py  # Gemini Vision client
    ├── image_handler.py       # Image processing
    └── rule_based_fallbacks.py  # Fallback responses
```

## 🌐 Deployment

### Streamlit Cloud (Recommended)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets (API keys) in Streamlit dashboard
5. Deploy!

**Voice features work perfectly on Streamlit Cloud (HTTPS)** ✅

## 🛠️ Technologies

- **Frontend**: Streamlit
- **AI Models**: 
  - Groq (llama-3.1-8b-instant) for text
  - Google Gemini Vision for image analysis
- **Voice**: Browser Native Web Speech API
- **Languages**: Python, JavaScript

## 📝 License

MIT License - feel free to use for your projects!

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or support, open an issue on GitHub.

---

**Made with ❤️ for Indian Farmers** 🌾
