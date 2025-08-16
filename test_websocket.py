#!/usr/bin/env python3
"""
WebSocket Test Client for AI Voice Agent

This script tests the WebSocket endpoint to ensure it's working correctly.
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    """Test the WebSocket endpoint with various message types"""
    uri = "ws://localhost:8000/ws"
    
    try:
        print("🔌 Connecting to WebSocket server...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Test 1: Simple text message
            print("\n📝 Test 1: Simple text message")
            await websocket.send("Hello, WebSocket!")
            response = await websocket.recv()
            print(f"📨 Response: {response}")
            
            # Test 2: JSON echo message
            print("\n📝 Test 2: JSON echo message")
            echo_message = {
                "type": "echo",
                "message": "This is a JSON echo test!"
            }
            await websocket.send(json.dumps(echo_message))
            response = await websocket.recv()
            print(f"📨 Response: {response}")
            
            # Test 3: Ping message
            print("\n📝 Test 3: Ping message")
            ping_message = {
                "type": "ping"
            }
            await websocket.send(json.dumps(ping_message))
            response = await websocket.recv()
            print(f"📨 Response: {response}")
            
            # Test 4: Status message
            print("\n📝 Test 4: Status request")
            status_message = {
                "type": "status"
            }
            await websocket.send(json.dumps(status_message))
            response = await websocket.recv()
            print(f"📨 Response: {response}")
            
            # Test 5: Unknown message type
            print("\n📝 Test 5: Unknown message type")
            unknown_message = {
                "type": "unknown",
                "message": "This is an unknown message type"
            }
            await websocket.send(json.dumps(unknown_message))
            response = await websocket.recv()
            print(f"📨 Response: {response}")
            
            print("\n🎉 All WebSocket tests completed successfully!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        print("💡 Make sure the server is running on http://localhost:8000")

if __name__ == "__main__":
    print("🚀 AI Voice Agent - WebSocket Test Client")
    print("=" * 50)
    asyncio.run(test_websocket())
