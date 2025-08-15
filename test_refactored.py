#!/usr/bin/env python3
"""
Test script for refactored AI Voice Agent

This script tests the new modular architecture to ensure all components work correctly.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our refactored modules
from schemas import TextRequest, TTSResponse, STTResponse, VoiceAgentResponse
from services import TTSService, STTService, LLMService, ChatManager
from utils import setup_logging, generate_session_id, validate_audio_file

def test_schemas():
    """Test Pydantic schemas"""
    print("🧪 Testing Pydantic Schemas...")
    
    # Test TextRequest
    text_req = TextRequest(text="Hello world", voice_id="en-US-1")
    assert text_req.text == "Hello world"
    
    # Test TTSResponse
    tts_resp = TTSResponse(status="success", audio_url="test.wav")
    assert tts_resp.status == "success"
    
    print("✅ All schemas working correctly!")

def test_utilities():
    """Test utility functions"""
    print("🧪 Testing Utility Functions...")
    
    # Test session ID generation
    session_id = generate_session_id()
    assert len(session_id) > 10
    
    # Test logging setup
    setup_logging()
    
    print("✅ All utilities working correctly!")

async def test_services():
    """Test service classes"""
    print("🧪 Testing Service Classes...")
    
    # Test TTS Service
    tts_service = TTSService()
    print(f"TTS Service Available: {tts_service.is_available()}")
    
    # Test STT Service
    stt_service = STTService()
    print(f"STT Service Available: {stt_service.is_available()}")
    
    # Test LLM Service
    llm_service = LLMService()
    print(f"LLM Service Available: {llm_service.is_available()}")
    
    # Test Chat Manager
    chat_manager = ChatManager()
    test_session = "test_session_123"
    chat_manager.add_message(test_session, "user", "Hello")
    chat_manager.add_message(test_session, "assistant", "Hi there!")
    
    history = chat_manager.get_history(test_session)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[1].role == "assistant"
    
    print("✅ All services initialized correctly!")

def test_environment_variables():
    """Test environment variable loading"""
    print("🧪 Testing Environment Variables...")
    
    required_vars = [
        "MURF_API_KEY",
        "ASSEMBLYAI_API_KEY", 
        "GOOGLE_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Add these to your .env file for full functionality")
    else:
        print("✅ All required environment variables found!")

async def main():
    """Run all tests"""
    print("🚀 Testing Refactored AI Voice Agent\n")
    
    test_schemas()
    test_utilities()
    await test_services()
    test_environment_variables()
    
    print("\n🎉 All tests completed successfully!")
    print("🔧 Your refactored AI Voice Agent is ready for Day 14 challenge!")

if __name__ == "__main__":
    asyncio.run(main())
