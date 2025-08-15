"""
Text-to-Speech Service using Murf API
"""
import os
import requests
import logging
from typing import Optional, Dict, Any
from schemas.models import TTSResponse

logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service using Murf API"""
    
    def __init__(self):
        self.api_key = os.getenv("MURF_API_KEY")
        self.base_url = "https://api.murf.ai/v1/speech/generate-with-key"
        self.timeout = 30
        
    def is_available(self) -> bool:
        """Check if TTS service is available"""
        return bool(self.api_key)
    
    async def generate_speech(self, text: str, voice_id: str = "en-US-marcus") -> TTSResponse:
        """
        Generate speech from text using Murf API
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use for generation
            
        Returns:
            TTSResponse with audio URL or error
        """
        if not self.api_key:
            logger.error("Murf API key not configured")
            return TTSResponse(
                status="error",
                error="TTS service not configured"
            )
        
        try:
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "voiceId": voice_id,
                "text": text,
                "format": "mp3"
            }
            
            logger.info(f"Generating TTS for text: {text[:50]}...")
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                audio_url = data.get("audioFile")
                
                if audio_url:
                    logger.info("TTS generation successful")
                    return TTSResponse(
                        status="success",
                        audio_url=audio_url,
                        message="Speech generated successfully"
                    )
                else:
                    logger.error("No audio file in TTS response")
                    return TTSResponse(
                        status="error",
                        error="No audio file generated"
                    )
            else:
                logger.error(f"TTS API error: {response.status_code} - {response.text}")
                return TTSResponse(
                    status="error",
                    error=f"TTS API error: {response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            logger.error("TTS request timeout")
            return TTSResponse(
                status="error",
                error="TTS service timeout"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS request failed: {str(e)}")
            return TTSResponse(
                status="error",
                error="TTS service unavailable"
            )
        except Exception as e:
            logger.error(f"Unexpected TTS error: {str(e)}")
            return TTSResponse(
                status="error",
                error="TTS generation failed"
            )
    
    async def generate_fallback_speech(self, message: str) -> Optional[str]:
        """Generate fallback TTS for error messages"""
        try:
            response = await self.generate_speech(message)
            if response.status == "success":
                return response.audio_url
            return None
        except Exception as e:
            logger.error(f"Fallback TTS failed: {str(e)}")
            return None
