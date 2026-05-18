import json
import requests
import os
import datetime
from groq import Groq
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()

def parler(texte):
    engine.say(texte)
    engine.runAndWait()

def ecouter():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("J'écoute...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("Rien entendu")
            return None
    try:
        texte = r.recognize_google(audio, language="fr-FR")
        print(f"{texte}")
        return texte
    except:
        print("Pas compris")
        return None

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
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

    Tu dois toujours inclure un champ "reponse" avec une réponse personnalisée et naturelle.

    Exemples :
    {{"action": "ouvrir_app", "device": "portable", "params": {{"app": "steam"}}, "reponse": "J'ouvre Steam dès maintenant, bonne session de jeu !"}}
    {{"action": "ouvrir_site", "device": "pc_fixe", "params": {{"url": "https://youtube.com"}}, "reponse": "J'ouvre YouTube pour vous."}}
    {{"action": "dire_heure", "device": "pc_fixe", "params": {{}}, "reponse": "Je vérifie l'heure pour vous."}}
    {{"action": "repondre", "device": "pc_fixe", "params": {{}}, "reponse": "Voici ma réponse à votre question."}}

    Toujours mettre une URL complète avec https://

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

message = ecouter()
if message:
    result = ask_jarvis(message)
    print(result)
    device = result.get("device", DEVICE)
    send_to_device(device, result)

    action = result["action"]
    reponse = result.get("reponse", "")

    if action == "dire_heure":
        heure = datetime.datetime.now().strftime("%H:%M")
        parler(f"Il est {heure}")
    else:
        parler(reponse)