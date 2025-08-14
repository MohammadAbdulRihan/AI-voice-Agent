# 🤖 AI Voice Assistant

**Click, talk, listen. It's that simple.**

> I got tired of typing to chatbots, so I built one you can actually talk to. 10 days of coffee-fueled coding later, here we are.

## What it does
- **Record** your voice with one button
- **Understands** what you said (AssemblyAI)  
- **Thinks** about it (Google Gemini AI)
- **Responds** in a natural voice (Murf TTS)
- **Remembers** your conversation

## Why it's different
Most voice demos break immediately. This one actually handles errors gracefully - when something goes wrong, it explains what happened instead of just crashing.

## Quick Start

**Prerequisites:** Python 3.8+, modern browser

```bash
git clone https://github.com/MohammadAbdulRihan/AI-voice-Agent.git
cd AI-voice-Agent
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Get API keys (all free to start):**
- [Google Gemini](https://aistudio.google.com/app/apikey) - Free AI brain
- [AssemblyAI](https://www.assemblyai.com/) - $50 free credit for speech-to-text  
- [Murf](https://murf.ai/) - Free trial for text-to-speech

**Create `.env` file:**
```env
MURF_API_KEY=your_murf_key
ASSEMBLYAI_API_KEY=your_assemblyai_key
GEMINI_API_KEY=your_gemini_key
```

**Run it:**
```bash
python app.py
```

Open `http://localhost:8000` and start talking!

## How to use
1. Click the big microphone button
2. Talk normally (don't sound like a robot)
3. Watch it think (cool animation!)
4. Listen to the AI respond
5. Keep the conversation going

## Tech Stack
- **Python + FastAPI** - Fast backend
- **Google Gemini** - AI brain (free!)
- **AssemblyAI** - Speech recognition
- **Murf** - Natural voice synthesis
- **Vanilla JavaScript** - Clean frontend

## What I learned
- FastAPI is really nice to work with
- Browser audio APIs are surprisingly powerful  
- Error handling is 80% of the work
- Making APIs play nice together takes patience
- Mobile audio behaves differently than desktop

## Troubleshooting

**Microphone not working?**
- Check browser permissions
- Refresh the page
- Make sure other apps aren't using your mic

**API key errors?**
- Double-check your `.env` file (no extra spaces!)
- Make sure you copied the complete key
- Try generating new keys

**AI acting weird?**
- APIs sometimes have bad days, just retry
- Check your internet connection
- The AI usually explains what's wrong

## Want to contribute?
Fork it, make it better, send a pull request. I'll probably accept it if it doesn't break everything.

**Ideas for improvements:**
- More voice options
- Real-time conversation (no recording delay)
- Multiple AI models
- Better mobile experience

## License
MIT - do whatever you want with it, just don't blame me if it breaks.

---

**Built by [Mohammad Abdul Rihan](https://github.com/MohammadAbdulRihan)**

*Many late nights and way too much coffee went into this ☕*

⭐ **Star this repo if it helped you!**
