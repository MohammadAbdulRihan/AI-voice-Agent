# 🧪 HOW TO TEST ERROR HANDLING - STEP BY STEP GUIDE

## 🌐 Method 1: Browser Testing (Easiest)

### Step 1: Open the Application
1. Make sure the server is running (you should see the startup messages)
2. Open your browser and go to: http://localhost:8000
3. You should see the AI Voice Agent interface

### Step 2: Test Normal Operation First
1. Click "🎤 Start Recording"
2. Say something (like "Hello, how are you?")
3. Click "🎤 Stop Recording"
4. Try each button to see normal operation:
   - "📝 Transcribe" - Should work if AssemblyAI key is valid
   - "🔄 Echo Bot v2" - Should work if both AssemblyAI and Murf keys are valid
   - "🤖 AI Chat" - Should work if all keys are valid
   - "💬 Conversation" - Should work if all keys are valid

### Step 3: Test Error Scenarios

#### 3a. Test Empty Audio Error
1. Click "🎤 Start Recording"
2. Immediately click "🎤 Stop Recording" (don't speak)
3. Try any voice function
4. Expected: "🎤 No audio detected or file is empty" message

#### 3b. Test Network Error
1. Open a new terminal
2. Stop the server (Ctrl+C in the server terminal)
3. Try any voice function in the browser
4. Expected: "🌐 Cannot connect to server" message
5. Restart the server

#### 3c. Test API Key Missing Error
1. Edit the .env file and comment out one API key:
   ```
   # ASSEMBLYAI_API_KEY=your_key_here
   ```
2. Try the transcription function
3. Expected: "🔧 API keys are missing or invalid" message

## 🔧 Method 2: API Testing with curl (Advanced)

### Test Endpoints Directly:

```bash
# Test transcription endpoint
curl -X POST http://localhost:8000/transcribe/file \
  -F "audio_file=@test_audio.wav"

# Test echo endpoint
curl -X POST http://localhost:8000/tts/echo \
  -F "audio_file=@test_audio.wav"

# Test AI chat endpoint
curl -X POST http://localhost:8000/llm/query \
  -F "audio_file=@test_audio.wav"

# Test conversation endpoint
curl -X POST http://localhost:8000/agent/chat/test_session \
  -F "audio_file=@test_audio.wav"
```

## 📊 Method 3: Check Server Logs

Watch the terminal where the server is running. You should see:

### Normal Operation:
```
INFO: 127.0.0.1:port - "POST /transcribe/file HTTP/1.1" 200 OK
```

### Error Scenarios:
```
WARNING: Missing API key for service: AssemblyAI
ERROR: Transcription failed: [specific error message]
INFO: Generated fallback audio for error: transcription_failed
```

## 🎯 What to Look For

### ✅ Success Indicators:
- Green status messages in browser
- Audio playback works
- Transcriptions appear correctly
- AI responses are generated

### ⚠️ Warning Indicators:
- Orange/yellow status messages
- "Partial success" notifications
- Text responses without audio

### ❌ Error Indicators:
- Red status messages
- Clear error descriptions
- Fallback audio explanations
- Recovery suggestions

## 🔍 Quick Status Check

### Check Current API Keys:
```bash
# Check if .env file has API keys
.\.venv\Scripts\python.exe -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('🔑 API Keys Status:')
print(f'Murf: {'✅' if os.getenv('MURF_API_KEY') else '❌'}')
print(f'AssemblyAI: {'✅' if os.getenv('ASSEMBLYAI_API_KEY') else '❌'}')
print(f'Google: {'✅' if os.getenv('GOOGLE_API_KEY') else '❌'}')
"
```

### Check Server Status:
```bash
# Test if server is responding
curl http://localhost:8000/
```

## 🎮 Interactive Testing Checklist

- [ ] ✅ Server starts without errors
- [ ] ✅ Browser interface loads
- [ ] ✅ Recording works (start/stop)
- [ ] ✅ Normal transcription works
- [ ] ✅ Echo bot works with voice
- [ ] ✅ AI chat generates responses
- [ ] ✅ Conversation maintains memory
- [ ] ⚠️ Empty audio shows proper error
- [ ] ⚠️ Missing API keys show clear messages
- [ ] ⚠️ Network errors are handled gracefully
- [ ] ⚠️ Partial failures show warnings
- [ ] ❌ All error types show user-friendly messages

## 🚀 Ready for Presentation!

Your application now handles all error scenarios professionally. During your presentation, you can:

1. **Demo normal operation** - Show the happy path
2. **Simulate an error** - Comment out an API key and show graceful handling
3. **Highlight robustness** - Explain how users never see technical errors
4. **Show recovery** - Demonstrate how the app guides users to fix issues

The error handling makes your AI Voice Agent **production-ready**! 🎉
