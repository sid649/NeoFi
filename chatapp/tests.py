import asyncio
import websockets

async def send_message():
    uri = "ws://localhost:8000/ws/chat/siddharth/"  # Replace <username> with the desired recipient's username
    async with websockets.connect(uri) as websocket:
        message = input("Enter a message to send: ")
        await websocket.send(message)
        print(f"Sent: {message}")
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.get_event_loop().run_until_complete(send_message())