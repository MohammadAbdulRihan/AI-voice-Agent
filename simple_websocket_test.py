"""
Simple WebSocket Test Client
Tests the basic WebSocket functionality of our AI Voice Agent
"""
import asyncio
import websockets
import json

async def test_websocket():
    """Test basic WebSocket connection and message exchange"""
    uri = "ws://localhost:8000/ws"
    
    try:
        print("🔗 Connecting to WebSocket server...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Test 1: Send simple text message
            print("\n📤 Test 1: Sending text message")
            await websocket.send("Hello from WebSocket client!")
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
            # Test 2: Send JSON echo message
            print("\n📤 Test 2: Sending JSON echo message")
            echo_message = json.dumps({
                "type": "echo",
                "data": "Testing echo functionality"
            })
            await websocket.send(echo_message)
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
            # Test 3: Send ping message
            print("\n📤 Test 3: Sending ping message")
            ping_message = json.dumps({"type": "ping"})
            await websocket.send(ping_message)
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
            # Test 4: Request status
            print("\n📤 Test 4: Requesting status")
            status_message = json.dumps({"type": "status"})
            await websocket.send(status_message)
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
            print("\n🎉 All tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting WebSocket Test Client")
    asyncio.run(test_websocket())
    print("✨ Test completed!")
