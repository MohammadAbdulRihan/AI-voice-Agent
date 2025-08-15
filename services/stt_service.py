"""
Speech-to-Text Service using AssemblyAI
"""
import os
import assemblyai as aai
import logging
from typing import Optional
from schemas.models import STTResponse

logger = logging.getLogger(__name__)

class STTService:
    """Speech-to-Text service using AssemblyAI"""
    
    def __init__(self):
        self.api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if self.api_key:
            aai.settings.api_key = self.api_key
        self.transcriber = aai.Transcriber() if self.api_key else None
        
    def is_available(self) -> bool:
        """Check if STT service is available"""
        return bool(self.api_key and self.transcriber)
    
    async def transcribe_audio(self, audio_file_path: str) -> STTResponse:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            STTResponse with transcript or error
        """
        if not self.is_available():
            logger.error("AssemblyAI API key not configured")
            return STTResponse(
                status="error",
                error="STT service not configured"
            )
        
        try:
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            # Transcribe the audio file
            transcript = self.transcriber.transcribe(audio_file_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                logger.error(f"Transcription failed: {transcript.error}")
                return STTResponse(
                    status="error",
                    error="Transcription failed"
                )
            
            if not transcript.text or transcript.text.strip() == "":
                logger.warning("No speech detected in audio")
                return STTResponse(
                    status="error",
                    error="No speech detected"
                )
            
            logger.info(f"Transcription successful: {transcript.text[:50]}...")
            return STTResponse(
                status="success",
                transcript=transcript.text,
                confidence=transcript.confidence if hasattr(transcript, 'confidence') else None
            )
            
        except Exception as e:
            logger.error(f"STT transcription error: {str(e)}")
            return STTResponse(
                status="error",
                error="Transcription service failed"
            )
    
    async def transcribe_url(self, audio_url: str) -> STTResponse:
        """
        Transcribe audio from URL
        
        Args:
            audio_url: URL to audio file
            
        Returns:
            STTResponse with transcript or error
        """
        if not self.is_available():
            return STTResponse(
                status="error",
                error="STT service not configured"
            )
        
        try:
            logger.info(f"Transcribing audio from URL: {audio_url}")
            transcript = self.transcriber.transcribe(audio_url)
            
            if transcript.status == aai.TranscriptStatus.error:
                return STTResponse(
                    status="error",
                    error="Transcription failed"
                )
            
            if not transcript.text:
                return STTResponse(
                    status="error", 
                    error="No speech detected"
                )
            
            return STTResponse(
                status="success",
                transcript=transcript.text,
                confidence=transcript.confidence if hasattr(transcript, 'confidence') else None
            )
            
        except Exception as e:
            logger.error(f"URL transcription error: {str(e)}")
            return STTResponse(
                status="error",
                error="Transcription service failed"
            )
