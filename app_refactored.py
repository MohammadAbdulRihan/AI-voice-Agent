"""
AI Voice Agent - Refactored FastAPI Application

Day 14: Code refactoring, clean architecture, and production readiness
- Separated services into dedicated modules
- Added comprehensive logging
- Created Pydantic schemas for all requests/responses  
- Improved error handling and code maintainability
- Organized code structure for scalability

Author: Mohammad Abdul Rihan
Repository: https://github.com/MohammadAbdulRihan/AI-voice-Agent
"""

import os
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Import our custom modules
from schemas import (
    TextRequest, TTSResponse, STTResponse, VoiceAgentResponse, 
    HealthResponse, ErrorResponse
)
from services import TTSService, STTService, LLMService, ChatManager
from utils import (
    setup_logging, generate_session_id, generate_filename, 
    ensure_upload_directory, validate_audio_file, get_env_variable,
    create_error_response, create_success_response
)

# =============================================================================
# APPLICATION SETUP
# =============================================================================

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Voice Agent",
    description="Production-ready voice-to-voice conversational AI with comprehensive error handling",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure upload directory exists
ensure_upload_directory()

# =============================================================================
# SERVICE INITIALIZATION
# =============================================================================

# Initialize services
tts_service = TTSService()
stt_service = STTService()
llm_service = LLMService()
chat_manager = ChatManager()

logger.info("AI Voice Agent services initialized")

# =============================================================================
# MIDDLEWARE & STARTUP EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("🚀 Starting AI Voice Agent Server...")
    logger.info("📊 Features: TTS, STT, LLM, Voice-to-Voice Chat, Conversational Memory")
    logger.info("🌐 Server will start at: http://localhost:8000")
    logger.info("💡 Open your browser and go to http://localhost:8000 to start using the AI Voice Agent!")
    
    # Check service availability
    services_status = {
        "TTS": "✅" if tts_service.is_available() else "❌",
        "STT": "✅" if stt_service.is_available() else "❌", 
        "LLM": "✅" if llm_service.is_available() else "❌"
    }
    
    logger.info(f"Services status: {services_status}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("🛑 Shutting down AI Voice Agent Server...")

# =============================================================================
# MAIN ROUTES
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main application interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {
        "tts": "available" if tts_service.is_available() else "unavailable",
        "stt": "available" if stt_service.is_available() else "unavailable",
        "llm": "available" if llm_service.is_available() else "unavailable"
    }
    
    all_available = all(status == "available" for status in services.values())
    
    return HealthResponse(
        status="healthy" if all_available else "degraded",
        message="All services operational" if all_available else "Some services unavailable",
        services=services,
        timestamp=datetime.now()
    )

# =============================================================================
# TTS ENDPOINTS
# =============================================================================

@app.post("/tts/generate", response_model=TTSResponse)
async def generate_tts(request: TextRequest):
    """Generate speech from text"""
    try:
        logger.info(f"TTS request for text: {request.text[:50]}...")
        
        if not request.text.strip():
            return TTSResponse(
                status="error",
                error="Empty text provided"
            )
        
        response = await tts_service.generate_speech(request.text, request.voice_id)
        return response
        
    except Exception as e:
        logger.error(f"TTS endpoint error: {str(e)}")
        return TTSResponse(
            status="error",
            error="TTS service failed"
        )

@app.post("/tts/echo", response_model=TTSResponse)
async def echo_tts(request: TextRequest):
    """Echo bot with TTS response"""
    try:
        echo_text = f"You said: {request.text}"
        response = await tts_service.generate_speech(echo_text)
        
        if response.status == "success":
            response.message = f"Echo: {request.text}"
            
        return response
        
    except Exception as e:
        logger.error(f"Echo TTS error: {str(e)}")
        return TTSResponse(
            status="error",
            error="Echo service failed"
        )

# =============================================================================
# STT ENDPOINTS  
# =============================================================================

@app.post("/transcribe/file", response_model=STTResponse)
async def transcribe_audio_file(audio_file: UploadFile = File(...)):
    """Transcribe uploaded audio file"""
    try:
        logger.info(f"STT request for file: {audio_file.filename}")
        
        # Validate file
        if not audio_file.filename:
            return STTResponse(
                status="error",
                error="No file provided"
            )
        
        # Save uploaded file
        filename = generate_filename(extension="webm")
        file_path = Path("uploads") / filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        # Validate saved file
        if not validate_audio_file(str(file_path)):
            file_path.unlink(missing_ok=True)
            return STTResponse(
                status="error",
                error="Invalid or empty audio file"
            )
        
        # Transcribe
        response = await stt_service.transcribe_audio(str(file_path))
        
        # Cleanup
        file_path.unlink(missing_ok=True)
        
        return response
        
    except Exception as e:
        logger.error(f"STT endpoint error: {str(e)}")
        return STTResponse(
            status="error",
            error="Transcription service failed"
        )

# =============================================================================
# LLM ENDPOINTS
# =============================================================================

@app.post("/llm/query", response_model=VoiceAgentResponse)
async def llm_query_with_voice(audio_file: UploadFile = File(...)):
    """Process voice input through full AI pipeline"""
    session_id = generate_session_id()
    
    try:
        logger.info(f"LLM voice query for session: {session_id}")
        
        # Step 1: Save and validate audio
        filename = generate_filename()
        file_path = Path("uploads") / filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        if not validate_audio_file(str(file_path)):
            file_path.unlink(missing_ok=True)
            return VoiceAgentResponse(
                status="error",
                error_type="empty_audio",
                fallback_message="No audio detected. Please record a clear message."
            )
        
        # Step 2: Transcribe audio
        stt_response = await stt_service.transcribe_audio(str(file_path))
        file_path.unlink(missing_ok=True)
        
        if stt_response.status != "success":
            fallback_audio = await tts_service.generate_fallback_speech(
                "Speech recognition failed. Please speak clearly and try again."
            )
            return VoiceAgentResponse(
                status="error",
                error_type="transcription_failed", 
                fallback_message="Speech recognition failed. Please speak clearly and try again.",
                audio_url=fallback_audio
            )
        
        user_message = stt_response.transcript
        
        # Step 3: Generate AI response
        llm_response = await llm_service.generate_response(user_message)
        
        if llm_response.status != "success":
            fallback_audio = await tts_service.generate_fallback_speech(
                "My AI brain is having trouble right now. Please try again in a moment."
            )
            return VoiceAgentResponse(
                status="error",
                error_type="llm_error",
                user_message=user_message,
                fallback_message="My AI brain is having trouble right now. Please try again in a moment.",
                audio_url=fallback_audio
            )
        
        ai_response = llm_response.response
        
        # Step 4: Generate voice response
        tts_response = await tts_service.generate_speech(ai_response)
        
        if tts_response.status == "success":
            return VoiceAgentResponse(
                status="success",
                user_message=user_message,
                assistant_message=ai_response,
                audio_url=tts_response.audio_url,
                session_id=session_id,
                timestamp=datetime.now()
            )
        else:
            return VoiceAgentResponse(
                status="partial_success",
                user_message=user_message,
                assistant_message=ai_response,
                fallback_message="AI responded but voice synthesis failed",
                session_id=session_id,
                timestamp=datetime.now()
            )
            
    except Exception as e:
        logger.error(f"LLM pipeline error: {str(e)}")
        fallback_audio = await tts_service.generate_fallback_speech(
            "Something went wrong with my processing. Please try again."
        )
        return VoiceAgentResponse(
            status="error",
            error_type="pipeline_error",
            fallback_message="Something went wrong with my processing. Please try again.",
            audio_url=fallback_audio,
            session_id=session_id
        )

# =============================================================================
# CONVERSATIONAL AGENT ENDPOINTS
# =============================================================================

@app.post("/agent/chat/{session_id}", response_model=VoiceAgentResponse)
async def conversational_voice_agent(session_id: str, audio_file: UploadFile = File(...)):
    """Complete conversational voice agent with memory"""
    try:
        logger.info(f"Conversational agent request for session: {session_id}")
        
        # Check service availability
        if not all([tts_service.is_available(), stt_service.is_available(), llm_service.is_available()]):
            missing_services = []
            if not tts_service.is_available(): missing_services.append("TTS")
            if not stt_service.is_available(): missing_services.append("STT") 
            if not llm_service.is_available(): missing_services.append("LLM")
            
            error_msg = f"Required services unavailable: {', '.join(missing_services)}. Please check your API keys."
            fallback_audio = await tts_service.generate_fallback_speech(error_msg)
            
            return VoiceAgentResponse(
                status="error",
                error_type="api_keys_missing",
                fallback_message=error_msg,
                audio_url=fallback_audio,
                session_id=session_id
            )
        
        # Step 1: Process audio file
        filename = generate_filename()
        file_path = Path("uploads") / filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        if not validate_audio_file(str(file_path)):
            file_path.unlink(missing_ok=True)
            error_msg = "No audio detected. Please record a clear message and try again."
            fallback_audio = await tts_service.generate_fallback_speech(error_msg)
            
            return VoiceAgentResponse(
                status="error",
                error_type="empty_audio",
                fallback_message=error_msg,
                audio_url=fallback_audio,
                session_id=session_id
            )
        
        # Step 2: Speech-to-Text
        stt_response = await stt_service.transcribe_audio(str(file_path))
        file_path.unlink(missing_ok=True)
        
        if stt_response.status != "success":
            error_msg = "I couldn't understand what you said. Please speak clearly and try again."
            fallback_audio = await tts_service.generate_fallback_speech(error_msg)
            
            return VoiceAgentResponse(
                status="error",
                error_type="no_speech_detected" if "No speech" in str(stt_response.error) else "transcription_failed",
                fallback_message=error_msg,
                audio_url=fallback_audio,
                session_id=session_id
            )
        
        user_message = stt_response.transcript
        
        # Step 3: Get conversation history and generate LLM response
        chat_history = chat_manager.get_recent_context(session_id, max_messages=10)
        llm_response = await llm_service.generate_conversational_response(user_message, chat_history)
        
        if llm_response.status != "success":
            error_msg = "My AI brain is having trouble right now. Please try again in a moment."
            fallback_audio = await tts_service.generate_fallback_speech(error_msg)
            
            return VoiceAgentResponse(
                status="error",
                error_type="llm_error",
                user_message=user_message,
                fallback_message=error_msg,
                audio_url=fallback_audio,
                session_id=session_id
            )
        
        ai_response = llm_response.response
        
        # Step 4: Save to chat history
        chat_manager.add_message(session_id, "user", user_message)
        chat_manager.add_message(session_id, "assistant", ai_response)
        
        # Step 5: Generate speech response
        tts_response = await tts_service.generate_speech(ai_response)
        
        if tts_response.status == "success":
            logger.info(f"Complete conversation successful for session: {session_id}")
            return VoiceAgentResponse(
                status="success",
                user_message=user_message,
                assistant_message=ai_response,
                audio_url=tts_response.audio_url,
                session_id=session_id,
                timestamp=datetime.now()
            )
        else:
            logger.warning(f"TTS failed but conversation succeeded for session: {session_id}")
            return VoiceAgentResponse(
                status="partial_success", 
                user_message=user_message,
                assistant_message=ai_response,
                fallback_message="I can respond but my voice synthesis isn't working right now.",
                session_id=session_id,
                timestamp=datetime.now()
            )
            
    except Exception as e:
        logger.error(f"Conversational agent error: {str(e)}")
        error_msg = "Something unexpected happened. Please try again."
        fallback_audio = await tts_service.generate_fallback_speech(error_msg)
        
        return VoiceAgentResponse(
            status="error",
            error_type="unexpected_error",
            fallback_message=error_msg,
            audio_url=fallback_audio,
            session_id=session_id
        )

@app.get("/agent/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = chat_manager.get_history_as_dict(session_id)
        return create_success_response(
            {"session_id": session_id, "messages": history, "count": len(history)},
            "Chat history retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        return create_error_response("history_error", "Failed to retrieve chat history")

# =============================================================================
# FILE MANAGEMENT ENDPOINTS
# =============================================================================

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and save audio file"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        filename = generate_filename()
        file_path = Path("uploads") / filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded successfully: {filename}")
        return create_success_response(
            {"filename": filename, "path": str(file_path)},
            "File uploaded successfully"
        )
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="File upload failed")

@app.get("/files/{filename}")
async def get_file(filename: str):
    """Download file by filename"""
    try:
        file_path = Path("uploads") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            media_type="audio/wav",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="File retrieval failed")

@app.get("/files")
async def file_manager(request: Request):
    """File management interface"""
    return templates.TemplateResponse("file_manager.html", {"request": request})

# =============================================================================
# LEGACY COMPATIBILITY ENDPOINTS
# =============================================================================

@app.get("/api/hello")
async def hello():
    """Legacy compatibility endpoint"""
    return {"message": "AI Voice Agent API is running", "status": "success", "version": "2.0.0"}

@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint"""
    return {"message": "No favicon configured"}

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    host = get_env_variable("HOST", "0.0.0.0")
    port = int(get_env_variable("PORT", "8000"))
    debug = get_env_variable("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
