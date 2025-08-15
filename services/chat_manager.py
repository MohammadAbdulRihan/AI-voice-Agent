"""
Chat Session Management Service
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from schemas.models import ChatMessage

logger = logging.getLogger(__name__)

class ChatManager:
    """Manages chat sessions and conversation history"""
    
    def __init__(self):
        self.sessions: Dict[str, List[ChatMessage]] = {}
        self.max_history_length = 50  # Maximum messages per session
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to chat session
        
        Args:
            session_id: Unique session identifier
            role: "user" or "assistant"
            content: Message content
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            logger.info(f"Created new chat session: {session_id}")
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        
        self.sessions[session_id].append(message)
        
        # Trim history if too long
        if len(self.sessions[session_id]) > self.max_history_length:
            self.sessions[session_id] = self.sessions[session_id][-self.max_history_length:]
            logger.info(f"Trimmed chat history for session {session_id}")
        
        logger.info(f"Added {role} message to session {session_id}")
    
    def get_history(self, session_id: str) -> List[ChatMessage]:
        """
        Get chat history for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of chat messages
        """
        return self.sessions.get(session_id, [])
    
    def get_history_as_dict(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get chat history as dictionary list for LLM context
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dictionaries
        """
        messages = self.get_history(session_id)
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear chat history for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session existed and was cleared
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared chat session: {session_id}")
            return True
        return False
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self.sessions)
    
    def get_message_count(self, session_id: str) -> int:
        """Get message count for specific session"""
        return len(self.sessions.get(session_id, []))
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        return session_id in self.sessions
    
    def get_recent_context(self, session_id: str, max_messages: int = 10) -> List[Dict[str, str]]:
        """
        Get recent conversation context for LLM
        
        Args:
            session_id: Session identifier
            max_messages: Maximum number of recent messages
            
        Returns:
            List of recent message dictionaries
        """
        messages = self.get_history_as_dict(session_id)
        return messages[-max_messages:] if messages else []
