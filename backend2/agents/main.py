from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from audio import speak_async
import json
from nova import ask_nova

import requests

app =FastAPI()


get_ip = {
    "pc_fixe": "192.168.1.18:5001",
}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connecté")
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)  # transforme la string JSON en dict Python
            texte = payload.get("user_message", "")
            voice_target = payload.get("voice_target", "serveur")

            if texte and "nova" in texte.lower():
                commande = texte.lower().replace("nova", "").strip()


                result = ask_nova(commande)
                if voice_target == "serveur":
                    await websocket.send_json({"type": "speech", "text": result})
                    await speak_async(result)

                else :
                    await websocket.send_json({"type": "text", "text": result})

                    url = f"http://{get_ip.get(voice_target)}/speak"
                    try :
                        requests.post(url,json={"text":result},timeout=5)
                    except Exception as e:
                        print(f"Agent injoignable : {e}")


    except WebSocketDisconnect:
        print("WebSocket deconnecté")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)