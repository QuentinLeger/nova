import requests
import speech_recognition as sr


def parler(texte, device):
    IPS = {
        "pc_fixe": "192.168.1.18:5001",
        "pc_portable": "10.13.33.131:5001"
    }
    ip = IPS.get(device, "10.13.33.131:5001")
    print(f"[PARLER] device={device}, ip={ip}, texte={texte}")  # debug
    try:
        r = requests.post(f"http://{ip}/speak", json={"text": texte}, timeout=10)
        print(f"[PARLER] status={r.status_code}")  # debug
    except Exception as e:
        print(f"[PARLER] ERREUR : {e}")
        print(f"Nova : {texte}")

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
        print(f"Vous : {texte}")
        return texte
    except:
        print("Pas compris")
        return None