"""
Ultra Simple WebSocket Test
Tests basic connection without complex asyncio
"""
import asyncio
import websockets
import json
import time

async def simple_test():
    """Simple WebSocket test"""
    try:
        print("Connecting to ws://localhost:8000/ws...")
        websocket = await websockets.connect("ws://localhost:8000/ws")
        print("Connected!")
        
        # Send a simple message
        await websocket.send("Hello WebSocket!")
        response = await websocket.recv()
        print(f"Received: {response}")
        
        # Send JSON message
        json_msg = json.dumps({"type": "ping"})
        await websocket.send(json_msg)
        response = await websocket.recv()
        print(f"Ping response: {response}")
        
        await websocket.close()
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

# Run the test
print("Starting WebSocket test...")
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(simple_test())
loop.close()
print("Done!")
