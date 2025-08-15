"""
Pydantic schemas for request/response models
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class TextRequest(BaseModel):
    """Request model for text-to-speech"""
    text: str
    voice_id: Optional[str] = "en-US-marcus"

class TTSResponse(BaseModel):
    """Response model for TTS operations"""
    status: str
    audio_url: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

class STTResponse(BaseModel):
    """Response model for speech-to-text"""
    status: str
    transcript: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None

class LLMResponse(BaseModel):
    """Response model for LLM operations"""
    status: str
    response: Optional[str] = None
    error: Optional[str] = None

class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class VoiceAgentResponse(BaseModel):
    """Complete voice agent response"""
    status: str  # "success", "partial_success", "error"
    user_message: Optional[str] = None
    assistant_message: Optional[str] = None
    audio_url: Optional[str] = None
    session_id: Optional[str] = None
    error_type: Optional[str] = None
    fallback_message: Optional[str] = None
    timestamp: Optional[datetime] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    services: Dict[str, str]
    timestamp: datetime

class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()
