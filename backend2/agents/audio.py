import os
import pygame
from gtts import gTTS
import speech_recognition as sr

def ecouter():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=2)
        print("Je vous écoute")
        try:
            audio = r.listen(source, timeout=2)
        except sr.WaitTimeoutError:
            print("Rien entendu")
            return None

    try:
        text = r.recognize_google(audio, language="fr-FR")
        print(f"Vous : {text}")
        return text
    except Exception:
        print("Je n'ai pas compris votre requête")
        return None


async def generer_voix(texte):
    # Remplacement temporaire avec gTTS (accent fr standard)
    tts = gTTS(text=texte, lang="fr", slow=False)
    tts.save("output.mp3")


def jouer_audio():
    pygame.mixer.init()
    pygame.mixer.music.unload()
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
    pygame.mixer.quit()


async def speak_async(texte):
    await generer_voix(texte)
    jouer_audio()