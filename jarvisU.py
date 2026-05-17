import json
import requests
import os
from groq import Groq
from dotenv import load_dotenv


load_dotenv()  # charge ton fichier .env automatiquement

api_key = os.getenv("GROQ_API_KEY")

print(api_key)  # juste pour vérifier


client = Groq(api_key=api_key)
DEVICE = "pc_fixe"


def ask_jarvis(message: str):
    prompt = f"""
Tu es Jarvis. Réponds UNIQUEMENT en JSON valide.

Actions possibles :
- ouvrir_site
- dire_heure
- repondre
- ouvrir_app

Si l'utilisateur mentionne un appareil (pc fixe, portable, tv, lumiere, etc.),
tu renvoies un champ "device". Sinon device = "pc_fixe".

Exemple :
{{"action": "ouvrir_app", "device": "portable", "params": {{"app": "steam"}}}}

Phrase : "{message}"
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content
    return json.loads(text)


def send_to_device(device, payload):
    DEVICE_IPS = {
        "pc_fixe": "192.168.1.18:5001"
    }

    url = f"http://{DEVICE_IPS[device]}/execute"
    requests.post(url, json=payload)


# -----------------------------
# PROGRAMME PRINCIPAL
# -----------------------------

message = input("Requete : ")
result = ask_jarvis(message)
print(result)
print()

device = result.get("device", DEVICE)
send_to_device(device, result)
