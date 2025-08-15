"""
Large Language Model Service using Google Gemini
"""
import os
import google.generativeai as genai
import logging
from typing import Optional, List, Dict
from schemas.models import LLMResponse

logger = logging.getLogger(__name__)

class LLMService:
    """LLM service using Google Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            try:
                self.model = genai.GenerativeModel(self.model_name)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {str(e)}")
                self.model = None
        else:
            self.model = None
    
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return bool(self.api_key and self.model)
    
    async def generate_response(self, prompt: str) -> LLMResponse:
        """
        Generate AI response to user prompt
        
        Args:
            prompt: User input text
            
        Returns:
            LLMResponse with AI response or error
        """
        if not self.is_available():
            logger.error("Gemini API not configured")
            return LLMResponse(
                status="error",
                error="LLM service not configured"
            )
        
        try:
            logger.info(f"Generating LLM response for: {prompt[:50]}...")
            
            # Generate response with Gemini
            response = self.model.generate_content(prompt)
            
            if response.text:
                logger.info("LLM response generated successfully")
                return LLMResponse(
                    status="success",
                    response=response.text
                )
            else:
                logger.error("Empty response from Gemini")
                return LLMResponse(
                    status="error",
                    error="No response generated"
                )
                
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            return LLMResponse(
                status="error",
                error="AI service temporarily unavailable"
            )
    
    async def generate_conversational_response(self, 
                                             user_message: str,
                                             chat_history: List[Dict[str, str]] = None) -> LLMResponse:
        """
        Generate conversational response with context
        
        Args:
            user_message: Current user message
            chat_history: Previous conversation history
            
        Returns:
            LLMResponse with contextual AI response
        """
        if not self.is_available():
            return LLMResponse(
                status="error",
                error="LLM service not configured"
            )
        
        try:
            # Build conversation context
            conversation_prompt = self._build_conversation_prompt(user_message, chat_history)
            
            logger.info("Generating conversational response with context")
            response = self.model.generate_content(conversation_prompt)
            
            if response.text:
                return LLMResponse(
                    status="success",
                    response=response.text
                )
            else:
                return LLMResponse(
                    status="error",
                    error="No response generated"
                )
                
        except Exception as e:
            logger.error(f"Conversational LLM error: {str(e)}")
            return LLMResponse(
                status="error",
                error="AI service temporarily unavailable"
            )
    
    def _build_conversation_prompt(self, user_message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Build conversation prompt with history context"""
        prompt = "You are a helpful AI assistant having a natural conversation. "
        prompt += "Respond in a friendly, conversational manner. Keep responses concise but helpful.\n\n"
        
        if chat_history:
            prompt += "Previous conversation:\n"
            for msg in chat_history[-10:]:  # Only use last 10 messages for context
                if msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"
        
        prompt += f"\nUser: {user_message}\nAssistant:"
        return prompt
