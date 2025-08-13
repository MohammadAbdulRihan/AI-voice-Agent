# =============================================================================
# AI VOICE AGENT - BACKEND SERVER (app.py)
# =============================================================================
# 
# DAY 1: Basic FastAPI Setup
# DAY 2: Text-to-Speech Integration (Murf TTS API)
# DAY 3: Frontend Integration (HTML Templates & Static Files)
# DAY 4: Voice Recording (Echo Bot v1 - Browser MediaRecorder)
# DAY 5: File Upload to Server (Audio Storage & Management)
# DAY 6: Speech-to-Text Transcription (AssemblyAI Integration)
# DAY 7: Echo Bot v2 (Voice Processing Pipeline)
# DAY 8: LLM Integration (Google Gemini API)
# DAY 9: Voice-to-Voice AI Chat (Complete Audio Pipeline)
# DAY 10: Chat History & Conversational Memory (Session Management)
#
# =============================================================================

# DAY 1: Basic Imports for FastAPI Server
import os
import requests
from dotenv import load_dotenv                    # DAY 2: Environment variables
from fastapi import FastAPI, Request, HTTPException, UploadFile, File  # DAY 1 + DAY 5
from fastapi.responses import HTMLResponse        # DAY 3: HTML responses
from fastapi.staticfiles import StaticFiles      # DAY 3: Static file serving
from fastapi.templating import Jinja2Templates   # DAY 3: Template engine
from pydantic import BaseModel                   # DAY 2: Request models
import shutil                                    # DAY 5: File operations
from pathlib import Path                         # DAY 5: Path handling
import assemblyai as aai                         # DAY 6: Speech-to-text
import google.generativeai as genai             # DAY 8: LLM integration
from typing import List, Dict                    # DAY 10: Type hints for chat storage
from datetime import datetime                    # DAY 10: Timestamps for messages

# DAY 2: Load environment variables from .env file
load_dotenv()

# =============================================================================
# GLOBAL HELPER FUNCTIONS
# =============================================================================

async def generate_fallback_tts(message: str):
    """Generate TTS for fallback messages if possible"""
    if not MURF_API_KEY:
        return None
    
    try:
        headers = {"api-key": MURF_API_KEY, "Content-Type": "application/json"}
        payload = {"voiceId": "en-US-marcus", "text": message, "format": "mp3"}
        
        response = requests.post(MURF_TTS_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("audioFile")
    except:
        return None

# =============================================================================
# DAY 10: CHAT HISTORY STORAGE (Session Management)
# =============================================================================
# In-memory datastore for chat history (session_id -> list of messages)
chat_sessions: Dict[str, List[Dict]] = {}

def add_message_to_session(session_id: str, role: str, content: str):
    """Add a message to the chat session history"""
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    message = {
        "role": role,  # "user" or "assistant"
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    chat_sessions[session_id].append(message)

def get_session_history(session_id: str) -> List[Dict]:
    """Get the chat history for a session"""
    return chat_sessions.get(session_id, [])

def format_history_for_llm(session_id: str, new_user_message: str) -> str:
    """Format chat history + new message for LLM context"""
    history = get_session_history(session_id)
    
    # Build conversation context
    conversation = "You are a helpful AI assistant having a conversation. Here's our chat history:\n\n"
    
    for msg in history:
        if msg["role"] == "user":
            conversation += f"User: {msg['content']}\n"
        else:
            conversation += f"Assistant: {msg['content']}\n"
    
    # Add the new user message
    conversation += f"User: {new_user_message}\n"
    conversation += "Assistant:"
    
    return conversation

# =============================================================================
# DAY 1: BASIC FASTAPI SERVER SETUP
# =============================================================================

app = FastAPI(title="AI Voice Agent", description="Voice-to-Voice Conversational AI", version="1.0.0")

# DAY 3: Static files and templates setup for frontend integration
# This tells the server where to find your 'static' files (like script.js)
app.mount("/static", StaticFiles(directory="static"), name="static")

# This sets up the template engine to find your HTML files
templates = Jinja2Templates(directory="templates")

# DAY 3: Main route that serves your HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# DAY 1: Simple endpoint to prevent 404 errors from old cached requests
@app.get("/api/hello")
async def hello():
    return {"message": "TTS API is running", "status": "success"}

# DAY 1: Favicon endpoint to prevent 404 errors
@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon configured"}

# =============================================================================
# DAY 2: API CONFIGURATIONS & MODELS
# =============================================================================

# DAY 2: The Pydantic model for the incoming JSON
class TextRequest(BaseModel):
    text: str

# DAY 2: Murf TTS API Configuration
MURF_API_KEY = os.getenv("MURF_API_KEY")
MURF_TTS_URL = "https://api.murf.ai/v1/speech/generate-with-key"

# DAY 6: AssemblyAI Configuration for Speech-to-Text
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
aai.settings.api_key = ASSEMBLYAI_API_KEY

# DAY 8: Google Gemini Configuration for LLM responses
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# =============================================================================
# DAY 2: TEXT-TO-SPEECH ENDPOINT (Murf TTS Integration)
# Enhanced with Robust Error Handling
# =============================================================================

@app.post("/generate-audio")
def generate_audio(request: TextRequest):
    """
    Text-to-Speech endpoint with comprehensive error handling and fallback responses
    """
    # Input validation
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # API key validation
    if not MURF_API_KEY:
        return {
            "status": "error",
            "error_type": "api_key_missing",
            "message": "TTS service temporarily unavailable - API key not configured",
            "fallback_message": "I'm having trouble with my voice service right now. Please try again later.",
            "audio_url": None
        }

    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "voiceId": "en-US-marcus",
        "text": request.text,
        "format": "mp3"
    }

    try:
        response = requests.post(MURF_TTS_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        audio_url = data.get("audioFile")
        if not audio_url:
            # Murf API response doesn't contain audio URL
            return {
                "status": "error",
                "error_type": "invalid_response",
                "message": "TTS service returned invalid response",
                "fallback_message": "I'm having trouble generating audio right now. Please try again.",
                "audio_url": None,
                "api_response": data
            }
        
        return {
            "status": "success",
            "audio_url": audio_url,
            "text": request.text,
            "voice_id": "en-US-marcus"
        }
        
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error_type": "timeout",
            "message": "TTS service timeout - request took too long",
            "fallback_message": "I'm taking too long to respond right now. Please try again in a moment.",
            "audio_url": None
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "error_type": "connection_error",
            "message": "Cannot connect to TTS service",
            "fallback_message": "I'm having trouble connecting to my voice service. Please check your internet connection.",
            "audio_url": None
        }
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else "unknown"
        return {
            "status": "error",
            "error_type": "http_error",
            "message": f"TTS API returned error {status_code}",
            "fallback_message": "My voice service is having issues right now. Please try again later.",
            "audio_url": None,
            "http_status": status_code
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_type": "request_error",
            "message": f"TTS API request failed: {str(e)}",
            "fallback_message": "I'm having trouble connecting right now. Please try again.",
            "audio_url": None
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "unexpected_error",
            "message": f"Unexpected error in TTS generation: {str(e)}",
            "fallback_message": "Something unexpected happened. Please try again.",
            "audio_url": None
        }

# --- AUDIO UPLOAD ENDPOINT ---

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

@app.post("/upload-audio")
async def upload_audio(audio_file: UploadFile = File(...)):
    """
    Upload endpoint that receives audio files from the echo bot,
    saves them temporarily, and returns file information.
    """
    try:
        # Validate file type (basic check)
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Generate a unique filename
        import uuid
        file_extension = ".webm"  # Default for our recorder
        if audio_file.filename:
            file_extension = Path(audio_file.filename).suffix or ".webm"
        
        unique_filename = f"recording_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = UPLOADS_DIR / unique_filename
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        # Get file size
        file_size = file_path.stat().st_size
        
        return {
            "status": "success",
            "message": "Audio file uploaded successfully",
            "filename": unique_filename,
            "content_type": audio_file.content_type,
            "size_bytes": file_size,
            "size_kb": round(file_size / 1024, 2),
            "upload_path": str(file_path)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# --- END OF UPLOAD ENDPOINT ---

# =============================================================================
# DAY 6: SPEECH-TO-TEXT TRANSCRIPTION ENDPOINT (AssemblyAI Integration)
# Enhanced with Robust Error Handling
# =============================================================================

@app.post("/transcribe/file")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Speech-to-Text endpoint with comprehensive error handling
    """
    # API key validation
    if not ASSEMBLYAI_API_KEY:
        return {
            "status": "error",
            "error_type": "api_key_missing",
            "message": "Speech recognition service unavailable - API key not configured",
            "fallback_message": "I can't understand audio right now. Please type your message instead.",
            "transcription": None
        }
    
    try:
        # File validation
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            return {
                "status": "error",
                "error_type": "invalid_file",
                "message": "Invalid audio file format",
                "fallback_message": "I couldn't process that audio file. Please try recording again.",
                "transcription": None
            }
        
        # Read audio data
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            return {
                "status": "error",
                "error_type": "empty_file",
                "message": "Audio file is empty",
                "fallback_message": "The audio recording seems to be empty. Please try recording again.",
                "transcription": None
            }
        
        # Transcribe with AssemblyAI
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_data)
        
        if transcript.status == aai.TranscriptStatus.error:
            return {
                "status": "error",
                "error_type": "transcription_failed",
                "message": f"AssemblyAI transcription failed: {transcript.error}",
                "fallback_message": "I couldn't understand what you said. Please try speaking more clearly.",
                "transcription": None
            }
        
        if not transcript.text or not transcript.text.strip():
            return {
                "status": "error",
                "error_type": "no_speech_detected",
                "message": "No speech detected in audio",
                "fallback_message": "I didn't hear any speech in that recording. Please try speaking louder.",
                "transcription": None
            }
        
        return {
            "status": "success",
            "transcription": transcript.text,
            "confidence": getattr(transcript, 'confidence', None),
            "audio_duration": getattr(transcript, 'audio_duration', None)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_type": "unexpected_error",
            "message": f"Unexpected error in transcription: {str(e)}",
            "fallback_message": "Something went wrong while processing your audio. Please try again.",
            "transcription": None
        }

# --- ECHO BOT v2 ENDPOINT ---

@app.post("/tts/echo")
async def echo_with_tts(audio_file: UploadFile = File(...)):
    """
    Echo Bot v2: Transcribe audio and respond with Murf TTS voice
    """
    # Step 1: Validate API keys
    if not ASSEMBLYAI_API_KEY:
        raise HTTPException(status_code=500, detail="AssemblyAI API key not configured")
    if not MURF_API_KEY:
        raise HTTPException(status_code=500, detail="Murf API key not configured")
    
    # Step 2: Transcribe the audio
    audio_data = await audio_file.read()
    transcript = aai.Transcriber().transcribe(audio_data)
    
    if transcript.status == aai.TranscriptStatus.error:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {transcript.error}")
    
    # Step 3: Generate TTS audio using Murf
    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "voiceId": "en-US-marcus",  # You can change this to any Murf voice
        "text": transcript.text,
        "format": "mp3"
    }
    
    try:
        response = requests.post(MURF_TTS_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Murf TTS API call failed: {e}")
    
    audio_url = data.get("audioFile")
    if not audio_url:
        raise HTTPException(status_code=500, detail=f"Audio URL not found in Murf API response: {data}")
    
    # Step 4: Return the transcription and audio URL
    return {
        "transcription": transcript.text,
        "audio_url": audio_url,
        "voice_id": "en-US-marcus"
    }

# --- END OF ECHO BOT v2 ENDPOINT ---

# --- LLM QUERY ENDPOINT (Voice-to-Voice) ---

@app.post("/llm/query")
async def query_llm_voice(audio_file: UploadFile = File(...)):
    """
    Voice-to-Voice AI Bot with comprehensive error handling and fallback TTS
    """
    try:
        # Step 1: Validate API keys
        missing_apis = []
        if not ASSEMBLYAI_API_KEY:
            missing_apis.append("AssemblyAI")
        if not GEMINI_API_KEY:
            missing_apis.append("Google")
        if not MURF_API_KEY:
            missing_apis.append("Murf")
        
        if missing_apis:
            fallback_message = f"API keys are missing for: {', '.join(missing_apis)}. Please check your configuration."
            fallback_audio = await generate_fallback_tts(fallback_message) if MURF_API_KEY else None
            
            return {
                "status": "error",
                "error_type": "api_keys_missing",
                "message": f"Missing API keys: {missing_apis}",
                "fallback_message": fallback_message,
                "audio_url": fallback_audio,
            }
        
        # Step 2: Transcribe the audio using AssemblyAI
        try:
            audio_data = await audio_file.read()
            if len(audio_data) == 0:
                fallback_message = "No audio detected or file is empty. Please record your voice and try again."
                fallback_audio = await generate_fallback_tts(fallback_message)
                
                return {
                    "status": "error",
                    "error_type": "empty_audio",
                    "message": "Audio file is empty",
                    "fallback_message": fallback_message,
                    "audio_url": fallback_audio,
                }
            
            transcript = aai.Transcriber().transcribe(audio_data)
            
            if transcript.status == aai.TranscriptStatus.error:
                fallback_message = "Speech recognition failed. Please speak clearly and try again."
                fallback_audio = await generate_fallback_tts(fallback_message)
                
                return {
                    "status": "error",
                    "error_type": "transcription_failed",
                    "message": f"Transcription failed: {transcript.error}",
                    "fallback_message": fallback_message,
                    "audio_url": fallback_audio,
                }
            
            if not transcript.text or not transcript.text.strip():
                fallback_message = "No speech detected in the audio. Please speak clearly and try again."
                fallback_audio = await generate_fallback_tts(fallback_message)
                
                return {
                    "status": "error",
                    "error_type": "no_speech_detected",
                    "message": "No speech detected in audio",
                    "fallback_message": fallback_message,
                    "audio_url": fallback_audio,
                }
            
        except Exception as e:
            fallback_message = "There was an issue processing your audio. Please try recording again."
            fallback_audio = await generate_fallback_tts(fallback_message)
            
            return {
                "status": "error",
                "error_type": "transcription_error",
                "message": f"Transcription error: {str(e)}",
                "fallback_message": fallback_message,
                "audio_url": fallback_audio,
            }
        
        # Step 3: Send transcription to Gemini LLM
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            llm_response = model.generate_content(transcript.text)
            
            if not llm_response.text:
                fallback_message = "I'm having trouble thinking right now. Please try again in a moment."
                fallback_audio = await generate_fallback_tts(fallback_message)
                
                return {
                    "status": "error",
                    "error_type": "empty_llm_response",
                    "message": "Empty response from Gemini API",
                    "fallback_message": fallback_message,
                    "audio_url": fallback_audio,
                }
            
        except Exception as e:
            fallback_message = "I'm having trouble connecting right now. Please try again."
            fallback_audio = await generate_fallback_tts(fallback_message)
            
            return {
                "status": "error",
                "error_type": "llm_error",
                "message": f"LLM error: {str(e)}",
                "fallback_message": fallback_message,
                "audio_url": fallback_audio,
            }
        
        # Step 4: Convert LLM response to speech using Murf TTS
        try:
            headers = {
                "api-key": MURF_API_KEY,
                "Content-Type": "application/json"
            }
            
            payload = {
                "voiceId": "en-US-marcus",
                "text": llm_response.text,
                "format": "mp3"
            }
            
            tts_response = requests.post(MURF_TTS_URL, json=payload, headers=headers, timeout=30)
            tts_response.raise_for_status()
            tts_data = tts_response.json()
            
            audio_url = tts_data.get("audioFile")
            if not audio_url:
                # Partial success - we have text but no audio
                return {
                    "status": "partial_success",
                    "user_query": transcript.text,
                    "llm_response": llm_response.text,
                    "audio_url": None,
                    "fallback_message": "AI responded but voice synthesis failed. Here's the text response.",
                    "model": "gemini-1.5-flash",
                    "voice_id": "en-US-marcus"
                }
            
            # Full success
            return {
                "status": "success",
                "user_query": transcript.text,
                "llm_response": llm_response.text,
                "audio_url": audio_url,
                "model": "gemini-1.5-flash",
                "voice_id": "en-US-marcus"
            }
            
        except Exception as e:
            # Partial success - we have text but TTS failed
            return {
                "status": "partial_success",
                "user_query": transcript.text,
                "llm_response": llm_response.text,
                "audio_url": None,
                "fallback_message": "AI responded but voice synthesis failed. Here's the text response.",
                "error_details": str(e),
                "model": "gemini-1.5-flash",
                "voice_id": "en-US-marcus"
            }
        
    except Exception as e:
        # Unexpected error
        fallback_message = "Something unexpected happened. Please try again."
        fallback_audio = await generate_fallback_tts(fallback_message) if MURF_API_KEY else None
        
        return {
            "status": "error",
            "error_type": "unexpected_error",
            "message": f"Unexpected error: {str(e)}",
            "fallback_message": fallback_message,
            "audio_url": fallback_audio,
        }

# --- END OF LLM QUERY ENDPOINT ---

# =============================================================================
# DAY 10: CONVERSATIONAL AGENT ENDPOINT (Enhanced Error Handling)
# Audio → STT → Chat History → LLM → TTS → Audio Response
# =============================================================================

@app.post("/agent/chat/{session_id}")
async def conversational_agent(session_id: str, audio_file: UploadFile = File(...)):
    """
    Conversational Agent with comprehensive error handling and fallback responses
    """
    
    # Step 1: Validate API keys
    missing_apis = []
    if not ASSEMBLYAI_API_KEY:
        missing_apis.append("Speech Recognition")
    if not GEMINI_API_KEY:
        missing_apis.append("AI Brain")
    if not MURF_API_KEY:
        missing_apis.append("Voice Generation")
    
    if missing_apis:
        fallback_message = f"I'm having trouble with my {', '.join(missing_apis)} service{'s' if len(missing_apis) > 1 else ''}. Please try again later."
        fallback_audio = await generate_fallback_tts(fallback_message) if MURF_API_KEY else None
        
        return {
            "status": "error",
            "error_type": "api_keys_missing",
            "message": f"Missing API keys: {', '.join(missing_apis)}",
            "fallback_message": fallback_message,
            "audio_url": fallback_audio,
            "session_id": session_id
        }
    
    try:
        # Step 2: Transcribe the audio using AssemblyAI
        try:
            audio_data = await audio_file.read()
            
            if len(audio_data) == 0:
                fallback_message = "I didn't receive any audio. Please try recording again."
                fallback_audio = await generate_fallback_tts(fallback_message)
                return {
                    "status": "error",
                    "error_type": "empty_audio",
                    "message": "Audio file is empty",
                    "fallback_message": fallback_message,
                    "audio_url": fallback_audio,
                    "session_id": session_id
                }
            
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_data)
            
            if transcript.status == aai.TranscriptStatus.error:
                fallback_message = "I couldn't understand what you said. Please try speaking more clearly."
                fallback_audio = await generate_fallback_tts(fallback_message)
                return {
                    "status": "error",
                    "error_type": "transcription_failed",
                    "message": f"Transcription failed: {transcript.error}",
                    "fallback_message": fallback_message,
                    "audio_url": fallback_audio,
                    "session_id": session_id
                }
            
            if not transcript.text or not transcript.text.strip():
                fallback_message = "I didn't hear any speech in that recording. Please try again."
                fallback_audio = await generate_fallback_tts(fallback_message)
                return {
                    "status": "error",
                    "error_type": "no_speech_detected",
                    "message": "No speech detected in audio",
                    "fallback_message": fallback_message,
                    "audio_url": fallback_audio,
                    "session_id": session_id
                }
            
            user_message = transcript.text.strip()
            
        except Exception as e:
            fallback_message = "I'm having trouble processing your audio right now. Please try again."
            fallback_audio = await generate_fallback_tts(fallback_message)
            return {
                "status": "error",
                "error_type": "transcription_error",
                "message": f"Audio processing failed: {str(e)}",
                "fallback_message": fallback_message,
                "audio_url": fallback_audio,
                "session_id": session_id
            }
        
        # Step 3: Get chat history and format for LLM with context
        conversation_context = format_history_for_llm(session_id, user_message)
        
        # Step 4: Send conversation context to Gemini LLM
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            llm_response = model.generate_content(conversation_context)
            
            if not llm_response.text or not llm_response.text.strip():
                fallback_message = "I'm having trouble thinking right now. Please try asking again."
                fallback_audio = await generate_fallback_tts(fallback_message)
                return {
                    "status": "error",
                    "error_type": "empty_llm_response",
                    "message": "Empty response from Gemini API",
                    "fallback_message": fallback_message,
                    "audio_url": fallback_audio,
                    "session_id": session_id,
                    "user_message": user_message
                }
            
            assistant_message = llm_response.text.strip()
            
        except Exception as e:
            fallback_message = "My AI brain is having trouble right now. Please try again in a moment."
            fallback_audio = await generate_fallback_tts(fallback_message)
            return {
                "status": "error",
                "error_type": "llm_error",
                "message": f"Gemini API failed: {str(e)}",
                "fallback_message": fallback_message,
                "audio_url": fallback_audio,
                "session_id": session_id,
                "user_message": user_message
            }
        
        # Step 5: Store both user and assistant messages in chat history
        add_message_to_session(session_id, "user", user_message)
        add_message_to_session(session_id, "assistant", assistant_message)
        
        # Step 6: Convert LLM response to speech using Murf TTS
        try:
            headers = {
                "api-key": MURF_API_KEY,
                "Content-Type": "application/json"
            }
            
            payload = {
                "voiceId": "en-US-marcus",
                "text": assistant_message,
                "format": "mp3"
            }
            
            tts_response = requests.post(MURF_TTS_URL, json=payload, headers=headers, timeout=30)
            tts_response.raise_for_status()
            tts_data = tts_response.json()
            
            audio_url = tts_data.get("audioFile")
            if not audio_url:
                # TTS failed, but we have the text response
                return {
                    "status": "partial_success",
                    "error_type": "tts_failed",
                    "message": "Voice generation failed, but text response is available",
                    "fallback_message": "I can think, but I'm having trouble speaking. Here's my response in text.",
                    "session_id": session_id,
                    "user_message": user_message,
                    "assistant_message": assistant_message,
                    "audio_url": None,
                    "conversation_length": len(get_session_history(session_id)),
                    "model": "gemini-1.5-flash"
                }
            
            # Step 7: Success! Return complete conversation flow
            return {
                "status": "success",
                "session_id": session_id,
                "user_message": user_message,
                "assistant_message": assistant_message,
                "audio_url": audio_url,
                "conversation_length": len(get_session_history(session_id)),
                "model": "gemini-1.5-flash",
                "voice_id": "en-US-marcus"
            }
            
        except Exception as e:
            # TTS failed, but we have the LLM response
            return {
                "status": "partial_success",
                "error_type": "tts_error",
                "message": f"Voice generation failed: {str(e)}",
                "fallback_message": "I can think, but I'm having trouble speaking right now.",
                "session_id": session_id,
                "user_message": user_message,
                "assistant_message": assistant_message,
                "audio_url": None,
                "conversation_length": len(get_session_history(session_id)),
                "model": "gemini-1.5-flash"
            }
        
    except Exception as e:
        # Catch-all for any unexpected errors
        fallback_message = "Something unexpected happened. Please try again."
        fallback_audio = await generate_fallback_tts(fallback_message)
        return {
            "status": "error",
            "error_type": "unexpected_error",
            "message": f"Unexpected error: {str(e)}",
            "fallback_message": fallback_message,
            "audio_url": fallback_audio,
            "session_id": session_id
        }

# --- GET CHAT HISTORY ENDPOINT ---

@app.get("/agent/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get the chat history for a session
    """
    history = get_session_history(session_id)
    return {
        "status": "success",
        "session_id": session_id,
        "messages": history,
        "message_count": len(history)
    }

# --- END OF CONVERSATIONAL AGENT ENDPOINTS ---

# --- FILE MANAGEMENT ENDPOINTS ---

@app.get("/list-uploads")
async def list_uploads():
    """
    List all uploaded audio files with their details
    """
    try:
        files = []
        for file_path in UPLOADS_DIR.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "size_bytes": stat.st_size,
                    "size_kb": round(stat.st_size / 1024, 2),
                    "upload_time": stat.st_mtime,
                    "file_path": str(file_path)
                })
        
        # Sort by upload time (newest first)
        files.sort(key=lambda x: x["upload_time"], reverse=True)
        
        return {
            "status": "success",
            "total_files": len(files),
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a specific uploaded audio file
    """
    from fastapi.responses import FileResponse
    
    file_path = UPLOADS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='audio/webm'
    )

# --- END OF FILE MANAGEMENT ENDPOINTS ---

# --- WEB INTERFACE FOR UPLOADED FILES ---

@app.get("/files", response_class=HTMLResponse)
async def view_files(request: Request):
    """
    Web interface to view and play uploaded audio files
    """
    return templates.TemplateResponse("files.html", {"request": request})

# --- END OF WEB INTERFACE ---

# =============================================================================
# DAY 1-10: APPLICATION STARTUP
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Voice Agent Server...")
    print("📊 Features: TTS, STT, LLM, Voice-to-Voice Chat, Conversational Memory")
    print("🌐 Server will start at: http://localhost:8000")
    print("💡 Open your browser and go to http://localhost:8000 to start using the AI Voice Agent!")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )