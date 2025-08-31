
# 🎙️ NovaVoice AI Voice Agent
# 🎙️ SpeakSync AI Voice Agent
A modern, production-ready voice-to-voice conversational AI agent with a sleek dark interface and robust architecture. Talk naturally with AI and get spoken responses in real-time.

## ✨ Features


## 🏗️ Architecture

### Service-Based Design

### Tech Stack

## 🚀 Quick Setup

### Prerequisites

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YourUsername/speaksync-ai-voice-agent.git
   cd speaksync-ai-voice-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**

   Copy the example environment file and add your API keys:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your API keys:
   ```env
   # AssemblyAI Configuration (Speech-to-Text)
   AssemblyAI_API_KEY=your_assemblyai_api_key_here

   # Google Gemini Configuration (Language Model)
   GOOGLE_API_KEY=your_google_gemini_api_key_here

   # Murf AI Configuration (Text-to-Speech)
   MURF_API_KEY=your_murf_api_key_here
   ```

4. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

5. **Open in browser**
   ```
   http://localhost:8000
   ```

## 🎮 Usage

1. Click the **microphone button** to start/stop recording
2. Speak clearly into your microphone
3. The AI will process your speech and respond with voice
4. Continue the conversation naturally

## 📁 Project Structure

```
novavoice-ai-voice-agent/
├── main.py              # FastAPI server with clean endpoint handlers
├── schemas.py           # Pydantic models for type safety
├── routes/              # Service layer architecture
│   ├── audio.py         # AssemblyAI speech-to-text service
│   ├── chat.py          # Google Gemini LLM service
│   └── system.py        # Murf AI text-to-speech service
├── static/
│   ├── style.css        # Modern dark theme
│   └── index.html       # Optimized voice interface
├── uploads/             # Audio uploads
├── .env                 # API configuration (create from .env.example)
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

## 🔧 API Endpoints

The application provides clean, type-safe API endpoints with Pydantic validation:


All endpoints return structured responses with proper error handling.

## 🔑 API Keys Setup

### AssemblyAI (Speech-to-Text)
1. Sign up at [AssemblyAI](https://www.assemblyai.com/)
2. Get your API key from the dashboard
3. Add to `.env` as `AssemblyAI_API_KEY`

### Google Gemini (Language Model)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a project and generate an API key
3. Add to `.env` as `GOOGLE_API_KEY`

### Murf AI (Text-to-Speech)
1. Register at [Murf AI](https://murf.ai/)
2. Subscribe to get API access
3. Add to `.env` as `MURF_API_KEY`

## 🚀 Development

**Local Development:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🎯 Recent Updates

### Code Quality Improvements

### Architecture Benefits