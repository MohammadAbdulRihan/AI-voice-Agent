# 🤖 MARVIS - AI Voice Assistant

MARVIS (Machine-based Assistant for Research, Voice, and Interactive Services) is a professional conversational AI voice assistant with a clean, modern interface.

## Features


## ✨ New & Improved Features

- 🖥️ **Modern Homepage UI**: Beautiful, professional landing page with hero section and animated gradients
- � **Glassmorphism & Gradient Effects**: Stylish glass cards, animated backgrounds, and feature pills for a premium look
- 📋 **Feature Pills Row**: Highlights agent capabilities in a visually appealing way
- 💬 **Sticky Chat Header**: Chat section with sticky header for context and status
- 🗨️ **Improved Chat Bubbles**: Modern, animated chat bubbles for user and AI messages
- 📱 **Fully Responsive Design**: Optimized for desktop and mobile, with adaptive layouts
- ⚙️ **Settings Sidebar**: Slide-out sidebar for API key management and agent configuration
- 🎨 **Custom Mascot & Branding**: SVG mascot and creative branding elements

- (All previous features retained)

   # Required for AI responses
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Optional TTS services (browser fallback available)
   OPENAI_API_KEY=your_openai_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_key_here
   MURF_API_KEY=your_murf_key_here
   
   # Optional (AssemblyAI has issues, browser speech works)
   ASSEMBLYAI_API_KEY=your_assemblyai_key_here
   ```

3. **Run the Application**:
   ```bash
   python start.py
   # or
   python main.py
   ```

4. **Open Your Browser**:
   Navigate to `http://localhost:8000`

## How to Use

1. **Click the microphone button** to start voice input
2. **Speak clearly** - MARVIS is listening!
3. **Or click the toggle button** to switch to text input
4. **Get intelligent responses** with natural conversation flow
5. **Continue the conversation** - MARVIS remembers your context!

## API Keys Setup

### Required:
- **Gemini API**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Optional (for better TTS):
- **OpenAI API**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **ElevenLabs API**: Get from [ElevenLabs](https://elevenlabs.io/)

## Technical Details

- **Backend**: FastAPI with WebSocket streaming
- **AI Model**: Google Gemini for pirate personality
- **Speech Recognition**: Browser Web Speech API (reliable)
- **TTS**: Multiple providers with browser fallback
- **Frontend**: Vanilla JavaScript with modern UI

## Troubleshooting

### Quick Fixes:
- **Speech recognition errors**: Use the "⌨️ Type Message" button as fallback
- **Network errors**: Use `http://localhost:8000` or HTTPS in production
- **Browser issues**: Chrome/Edge work best for speech recognition
- **No microphone**: Text input always available as backup

### Detailed Help:
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete solutions to common issues.

### Common Issues:
- **No speech detected**: Ensure microphone permissions are granted
- **AI not responding**: Check Gemini API key in `.env` file  
- **Audio not playing**: Browser TTS fallback should work on all devices

## Pirate Commands

Try saying:
- "Ahoy there, how are ye doing?"
- "Tell me about the seven seas"
- "What's the weather like on the high seas?"
- "Sing me a sea shanty!"

Arrr! Set sail on the seas of conversation, matey! 🏴‍☠️⚓