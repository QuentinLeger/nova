import json
import requests
import os
import datetime
from groq import Groq
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import subprocess



engine = pyttsx3.init()

def parler(texte):
    subprocess.call(["espeak-ng", "-v", "fr", texte])

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

    Tu es mon assitant vocal :D ton but est de maider au quotidien, dans mes taches, dans mes automatisations etc

    Actions possibles :
    - ouvrir_site
    - dire_heure
    - repondre
    - ouvrir_app
    - macro

    Si l'utilisateur mentionne un appareil (pc fixe, portable, tv, lumiere, etc.),
    tu renvoies un champ "device". Sinon device = "pc_fixe".

    Tu dois toujours inclure un champ "reponse" avec une réponse personnalisée et naturelle. Tu peux les faire plus longue et plus naturelle

    Exemples :
    {{"action": "ouvrir_app", "device": "portable", "params": {{"app": "steam"}}, "reponse": "J'ouvre Steam dès maintenant, bonne session de jeu !"}}
    {{"action": "ouvrir_site", "device": "pc_fixe", "params": {{"url": "https://youtube.com"}}, "reponse": "J'ouvre YouTube pour vous."}}
    {{"action": "dire_heure", "device": "pc_fixe", "params": {{}}, "reponse": "Je vérifie l'heure pour vous."}}
    {{"action": "repondre", "device": "pc_fixe", "params": {{}}, "reponse": "Voici ma réponse à votre question."}}

    Toujours mettre une URL complète avec https://

    Je peux aussi te demander des macro dans mes phrase par exemple pour streamer un jeu : 
    Les différentes macro possibles : 
    
    - coding
    - vibe-coding
    - stream
    
    Exemple : 
    {{"action": "macro", "device": "pc_fixe", "params": {{"nom": "stream_minecraft"}}, "reponse": "Je prépare tout pour ton stream Minecraft !"}}
    
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
while True:
    message = ecouter()
    if message and "jarvis" in message.lower():
        commande = message.lower().replace("jarvis", "").strip()
        if message:
            result = ask_jarvis(commande)
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