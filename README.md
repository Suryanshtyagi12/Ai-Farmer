# 🌱 AI Farming Assistant

An AI-powered web application helping farmers with crop recommendations, irrigation advice, and plant disease detection using expert AI models.

## 🌟 Features

- **Crop Suggestion**: Get personalized crop recommendations based on location, season, and soil format.
- **Irrigation Help**: Detailed irrigation plans including method, frequency, and schedule.
- **Disease & Pest Detection**: Upload a photo of a crop to detect diseases and get treatment advice.
- **Smart Talk (Voice Mode)**: Speak to the AI for advice using a hybrid voice interface (Voice Input + Audio Output).
- **Multilingual**: Full support for English and Hindi (हिंदी).

## 🚀 Tech Stack

- **Frontend**: Streamlit
- **LLM Reasoning**: Groq (Llama 3)
- **Vision Analysis**: Google Gemini 1.5 Flash
- **Voice**: Web Speech API (Input) + gTTS (Output)

## 🛠️ Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Suryanshtyagi12/Ai-Farmer.git
   cd Ai-Farmer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API Keys**
   - Create a `.env` file in the root directory
   - Add your API keys:
     ```
     GROQ_API_KEY=your_groq_api_key
     GEMINI_API_KEY=your_google_ai_key
     ```

4. **Run the App**
   ```bash
   streamlit run app.py
   ```

## ☁️ Deployment on Streamlit Cloud

1. Push this code to your GitHub repository.
2. Go to [Streamlit Cloud](https://share.streamlit.io/).
3. Connect your GitHub account and select this repository.
4. In "Advanced Settings", add your secrets:
   ```toml
   GROQ_API_KEY = "your_key_here"
   GEMINI_API_KEY = "your_key_here"
   ```
5. Click **Deploy**!

## 📜 License

MIT License
