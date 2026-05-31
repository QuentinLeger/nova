from flask import Flask, request
import subprocess
import webbrowser
import json
import requests
import asyncio
import edge_tts
import pygame
import os
from datetime import datetime
from dotenv import load_dotenv
from Notion import ajouter_tache, lister_taches, supprimer_tache

load_dotenv()
app = Flask(__name__)

with open("portable.json") as f:
    CONFIG = json.load(f)

async def generer_voix(texte):
    communicate = edge_tts.Communicate(texte, voice="fr-FR-VivienneMultilingualNeural", rate="+2%", pitch="-5Hz")
    await communicate.save("output.mp3")


@app.post("/speak")
def speak():
    texte = request.json["text"]

    pygame.mixer.init()
    pygame.mixer.music.unload()  # libère le fichier

    asyncio.run(generer_voix(texte))

    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    return {"status": "ok"}



@app.post("/save_file")
def save_file():
    nom = request.json["nom"]
    contenu = request.json["contenu"]
    chemin = f"C:/Users/atomi/OneDrive/Bureau/{nom}"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"Fichier sauvegardé : {chemin}")
    return {"status": "ok"}

def executer_action(data):
    action = data["action"]
    chrome = webbrowser.get("C:/Program Files/Google/Chrome/Application/chrome.exe %s")

    if action == "ouvrir_site":
        chrome.open(data["params"]["url"])

    elif action == "dire_heure":
        heure = datetime.now().strftime("%H:%M")
        print(f"Il est {heure}")

    elif action == "repondre":
        print(data["params"].get("reponse", ""))

    elif action == "ouvrir_app":
        app_name = data["params"]["app"]
        app_path = CONFIG["apps"].get(app_name)
        if app_path:
            subprocess.Popen(app_path)
        else:
            print(f"App inconnue : {app_name}")

    elif action == "macro":
        nom = data["params"]["nom"]
        macro = CONFIG["macros"].get(nom)
        if macro:
            for commande in macro:
                executer_action(commande)
        else:
            print(f"Macro inconnue : {nom}")

    elif action == "recherche_web":
        params = data["params"]
        type_rech = params.get("type")
        query = params.get("query", "").replace(" ", "+")

        if type_rech == "youtube":
            url = f"https://www.youtube.com/results?search_query={query}"
        elif type_rech == "google":
            url = f"https://www.google.com/search?q={query}"
        else:
            print("Type de recherche inconnu")
            return

        chrome.open(url)
        print(f"Recherche lancée : {url}")


    elif action == "gestion_taches":
        params = data["params"]
        type_action = params.get("type")

        if type_action == "add":
            titre = params.get("titre")
            date = params.get("date")
            result = ajouter_tache(titre, date)
            print(f"Notion response : {result}")  # debug complet


        elif type_action == "list" or type_action == "resume":

            taches = lister_taches()

            # Parse les tâches

            liste = []

            for t in taches.get("results", []):

                try:

                    nom = t["properties"]["Task name"]["title"][0]["text"]["content"]

                    statut = t["properties"]["Status"]["status"]["name"]

                    liste.append(f"{nom} ({statut})")

                except:

                    pass

            texte_taches = "\n".join(liste) if liste else "Aucune tâche trouvée"

            # Groq fait un résumé oral

            from groq import Groq

            from dotenv import load_dotenv

            load_dotenv()

            client = Groq(api_key=os.getenv("GROQ_API_KEY"))

            response = client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                messages=[{

                    "role": "user",

                    "content": f"""

        Voici les tâches de Quentin :

        {texte_taches}


        Fais un résumé oral court et naturel en 2-3 phrases.

        Parle à Quentin directement, sois concis.

                    """

                }]

            )

            resume = response.choices[0].message.content

            # Renvoie le résumé à Ubuntu pour qu'il parle

            requests.post("http://192.168.1.36:5001/speak", json={"text": resume})
        elif type_action == "delete":
            supprimer_tache(params.get("id"))
            print("Tâche supprimée")

@app.post("/execute")
def execute():
    executer_action(request.json)
    return {"status": "ok"}

app.run(host="0.0.0.0", port=5001)

