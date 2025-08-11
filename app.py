import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import shutil
from pathlib import Path
import assemblyai as aai
import google.generativeai as genai
from typing import List, Dict
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# --- CHAT HISTORY STORAGE ---
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

# --- END OF CHAT HISTORY STORAGE ---

# --- THIS IS THE DAY 1 CODE YOU NEED TO ADD BACK ---

app = FastAPI()

# This tells the server where to find your 'static' files (like script.js)
app.mount("/static", StaticFiles(directory="static"), name="static")

# This sets up the template engine to find your HTML files
templates = Jinja2Templates(directory="templates")

# This is the route that serves your HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Simple endpoint to prevent 404 errors from old cached requests
@app.get("/api/hello")
async def hello():
    return {"message": "TTS API is running", "status": "success"}

# Favicon endpoint to prevent 404 errors
@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon configured"}

# --- END OF DAY 1 CODE ---


# --- THIS IS YOUR DAY 2/3 API ENDPOINT CODE (IT'S ALREADY GOOD) ---

# The Pydantic model for the incoming JSON
class TextRequest(BaseModel):
    text: str

MURF_API_KEY = os.getenv("MURF_API_KEY")
MURF_TTS_URL = "https://api.murf.ai/v1/speech/generate-with-key"

# AssemblyAI Configuration
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
aai.settings.api_key = ASSEMBLYAI_API_KEY

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

@app.post("/generate-audio")
def generate_audio(request: TextRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

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
        response = requests.post(MURF_TTS_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Murf TTS API call failed: {e}")

    audio_url = data.get("audioFile")

    if not audio_url:
        raise HTTPException(status_code=500, detail=f"Audio URL not found in Murf API response: {data}")

    return {"audio_url": audio_url}

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

# --- TRANSCRIPTION ENDPOINT ---

@app.post("/transcribe/file")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    if not ASSEMBLYAI_API_KEY:
        raise HTTPException(status_code=500, detail="AssemblyAI API key not configured")
    
    audio_data = await audio_file.read()
    transcript = aai.Transcriber().transcribe(audio_data)
    
    if transcript.status == aai.TranscriptStatus.error:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {transcript.error}")
    
    return {"transcription": transcript.text}

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
    Voice-to-Voice AI Bot: Audio → Transcription → LLM → TTS → Audio Response
    """
    # Step 1: Validate API keys
    if not ASSEMBLYAI_API_KEY:
        raise HTTPException(status_code=500, detail="AssemblyAI API key not configured")
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    if not MURF_API_KEY:
        raise HTTPException(status_code=500, detail="Murf API key not configured")
    
    try:
        # Step 2: Transcribe the audio using AssemblyAI
        audio_data = await audio_file.read()
        transcript = aai.Transcriber().transcribe(audio_data)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {transcript.error}")
        
        if not transcript.text or not transcript.text.strip():
            raise HTTPException(status_code=400, detail="No speech detected in audio")
        
        # Step 3: Send transcription to Gemini LLM
        model = genai.GenerativeModel('gemini-1.5-flash')
        llm_response = model.generate_content(transcript.text)
        
        if not llm_response.text:
            raise HTTPException(status_code=500, detail="Empty response from Gemini API")
        
        # Step 4: Convert LLM response to speech using Murf TTS
        headers = {
            "api-key": MURF_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "voiceId": "en-US-marcus",
            "text": llm_response.text,
            "format": "mp3"
        }
        
        tts_response = requests.post(MURF_TTS_URL, json=payload, headers=headers)
        tts_response.raise_for_status()
        tts_data = tts_response.json()
        
        audio_url = tts_data.get("audioFile")
        if not audio_url:
            raise HTTPException(status_code=500, detail=f"Audio URL not found in Murf API response: {tts_data}")
        
        # Step 5: Return complete conversation flow
        return {
            "status": "success",
            "user_query": transcript.text,
            "llm_response": llm_response.text,
            "audio_url": audio_url,
            "model": "gemini-1.5-flash",
            "voice_id": "en-US-marcus"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(status_code=500, detail=f"Voice-to-Voice AI failed: {str(e)}")

# --- END OF LLM QUERY ENDPOINT ---

# --- CONVERSATIONAL AGENT ENDPOINT (Day 10) ---

@app.post("/agent/chat/{session_id}")
async def conversational_agent(session_id: str, audio_file: UploadFile = File(...)):
    """
    Conversational Agent with Chat History: Audio → STT → Chat History → LLM → TTS → Audio Response
    """
    # Step 1: Validate API keys
    if not ASSEMBLYAI_API_KEY:
        raise HTTPException(status_code=500, detail="AssemblyAI API key not configured")
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    if not MURF_API_KEY:
        raise HTTPException(status_code=500, detail="Murf API key not configured")
    
    try:
        # Step 2: Transcribe the audio using AssemblyAI
        audio_data = await audio_file.read()
        transcript = aai.Transcriber().transcribe(audio_data)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {transcript.error}")
        
        if not transcript.text or not transcript.text.strip():
            raise HTTPException(status_code=400, detail="No speech detected in audio")
        
        user_message = transcript.text.strip()
        
        # Step 3: Get chat history and format for LLM with context
        conversation_context = format_history_for_llm(session_id, user_message)
        
        # Step 4: Send conversation context to Gemini LLM
        model = genai.GenerativeModel('gemini-1.5-flash')
        llm_response = model.generate_content(conversation_context)
        
        if not llm_response.text:
            raise HTTPException(status_code=500, detail="Empty response from Gemini API")
        
        assistant_message = llm_response.text.strip()
        
        # Step 5: Store both user and assistant messages in chat history
        add_message_to_session(session_id, "user", user_message)
        add_message_to_session(session_id, "assistant", assistant_message)
        
        # Step 6: Convert LLM response to speech using Murf TTS
        headers = {
            "api-key": MURF_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "voiceId": "en-US-marcus",
            "text": assistant_message,
            "format": "mp3"
        }
        
        tts_response = requests.post(MURF_TTS_URL, json=payload, headers=headers)
        tts_response.raise_for_status()
        tts_data = tts_response.json()
        
        audio_url = tts_data.get("audioFile")
        if not audio_url:
            raise HTTPException(status_code=500, detail=f"Audio URL not found in Murf API response: {tts_data}")
        
        # Step 7: Return complete conversation flow with session info
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
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(status_code=500, detail=f"Conversational Agent failed: {str(e)}")

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