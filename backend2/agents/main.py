from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app =FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connecté")
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await websocket.send_json({"type": "speech", "text": "Message reçu !"})
    except WebSocketDisconnect:
        print("WebSocket deconnecté")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)