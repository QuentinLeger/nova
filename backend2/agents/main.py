from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from audio import speak_async
import json

app =FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connecté")
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)  # transforme la string JSON en dict Python
            texte = payload.get("user_message", "")

            await websocket.send_json({"type": "speech", "text": "Message reçu !"})
            await speak_async(texte)
    except WebSocketDisconnect:
        print("WebSocket deconnecté")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)