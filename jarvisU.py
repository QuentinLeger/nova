import json
import requests
import os
import socket
import subprocess
import speech_recognition as sr
import pyttsx3
import pandas as pd
from datetime import datetime, timedelta
from groq import Groq
from dotenv import load_dotenv
from Notion import ajouter_tache, lister_taches, supprimer_tache

load_dotenv()

def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

engine = pyttsx3.init()

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

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
DEVICE = "pc_fixe"

def ask_nova(message: str):
    prompt = f"""
    Tu es Nova. Réponds UNIQUEMENT en JSON valide.

    Tu es mon assistant vocal. Ton but est de m'aider au quotidien, dans mes tâches et automatisations.

    Actions possibles :
    - ouvrir_site
    - dire_heure
    - repondre
    - ouvrir_app
    - macro
    - analyse_seance
    - recherche_web
    - gestion_taches

    Pour analyse_seance : si je dis "ma séance" = today, "dernière séance" = last, "cette semaine" = week

    Si l'utilisateur mentionne un appareil (pc fixe, portable), tu renvoies un champ "device".
    Sinon device = "pc_fixe"
    Possibilité : pc_fixe, pc_portable

    Tu dois toujours inclure un champ "reponse" avec une réponse courte (1-2 phrases max).

    Exemples :
    {{"action": "ouvrir_app", "device": "pc_fixe", "params": {{"app": "steam"}}, "reponse": "J'ouvre Steam dès maintenant !"}}
    {{"action": "ouvrir_site", "device": "pc_fixe", "params": {{"url": "https://youtube.com"}}, "reponse": "J'ouvre YouTube pour vous."}}
    {{"action": "dire_heure", "device": "pc_fixe", "params": {{}}, "reponse": "Je vérifie l'heure."}}
    {{"action": "repondre", "device": "pc_fixe", "params": {{}}, "reponse": "Voici ma réponse."}}
    {{"action": "analyse_seance", "device": "pc_fixe", "params": {{"periode": "last"}}, "reponse": "J'analyse ta dernière séance !"}}
    {{"action": "macro", "device": "pc_fixe", "params": {{"nom": "stream_minecraft"}}, "reponse": "Je prépare tout pour ton stream Minecraft !"}}
    
    Pour recherche_web :
    - Si l’utilisateur dit "cherche counterStike sur YouTube", tu renvoies :
    {{"action": "recherche_web", "params": {{"type": "youtube", "query": "counterStrike"}}, "reponse": "......"}}
    
    - Si l’utilisateur dit "cherche quelquechose sur Google", tu renvoies :
    {{"action": "recherche_web", "params": {{"type": "google", "query": "quelquechose"}}, "reponse": "......"}}
    
    "ajoute une tâche" → {{"action": "gestion_taches", "params": {{"type": "add", "titre": "...", "date": "..."}} }}

    "liste mes tâches" → {{"action": "gestion_taches", "params": {{"type": "list"}} }}
    
    "supprime la tâche X" → {{"action": "gestion_taches", "params": {{"type": "delete", "id": "..."}} }}
    
    "qu’est-ce qu’il me reste à faire ?" → {{"action": "gestion_taches", "params": {{"type": "resume"}} }}

    Macros disponibles : coding, vibe-coding, stream
    Toujours mettre une URL complète avec https://
    Quand je dis "arche" c'est https://arche.univ-lorraine.fr/my/
    
    N'utilise JAMAIS d'apostrophes dans le champ "reponse". Utilise "Je" au lieu de "J'" etc.
    
    Tu t'appelles Nova, tu es mon assistante personnelle.
    Tu t'adresses à moi par mon prénom : Quentin.
    Tu es professionnelle mais chaleureuse, avec une légère touche d'humour.
    Tu utilises "vous" pour être élégante.
    Exemples de réponses :
    - "Bien sûr Quentin, je m'en occupe immédiatement."
    - "Voilà qui est fait, Quentin. Autre chose ?"
    - "Je lance ça pour vous, Quentin !"
    Tes réponses doivent être naturelles et fluides à l'oral.
    Utilise des virgules pour créer des pauses naturelles.
    Exemple : "Bien sur, je vous lance Steam pour vous Quentin. " et réponse personalisé genre voulez vous jouer etc ? 
    Plutôt que : "J'ouvre Steam dès maintenant."
    Tu t'appelles Nova, tu es l'assistante de Quentin.
    Tu es professionnelle, efficace, avec une légère touche d'humour.

    Phrase : "{message}"
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    print(f"[GROQ RAW] {text}")  # debug

    try:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "action": "repondre",
            "device": "pc_fixe",
            "params": {},
            "reponse": "Désolé, je n'ai pas compris."
        }

def send_to_device(device, payload):
    DEVICE_IPS = {
        "pc_fixe": "192.168.1.18:5001",
        "pc_portable": "10.13.33.131:5001"
    }
    if device not in DEVICE_IPS:
        device = DEVICE
    try:
        url = f"http://{DEVICE_IPS[device]}/execute"
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Appareil injoignable : {e}")

def analyser_seances(periode="last"):
    df = pd.read_csv("workouts.csv")
    df['start_time'] = pd.to_datetime(df['start_time'], format="%b %d, %Y, %I:%M %p")

    aujourd_hui = datetime.now().date()

    if periode == "today":
        df_filtre = df[df['start_time'].dt.date == aujourd_hui]
    elif periode == "week":
        debut_semaine = aujourd_hui - timedelta(days=7)
        df_filtre = df[df['start_time'].dt.date >= debut_semaine]
    elif periode == "last":
        df_filtre = df[df['start_time'] == df['start_time'].max()]
    else:
        df_filtre = df

    resume_historique = ""
    for (date, exercice), groupe in df.groupby(['start_time', 'exercise_title']):
        series = ", ".join([f"{r['weight_kg']}kg x{int(r['reps'])}" for _, r in groupe.iterrows()])
        resume_historique += f"{date} - {exercice}: {series}\n"

    resume_jour = ""
    for exercice, groupe in df_filtre.groupby('exercise_title'):
        series = ", ".join([f"{r['weight_kg']}kg x{int(r['reps'])}" for _, r in groupe.iterrows()])
        resume_jour += f"{exercice}: {series}\n"

    if not resume_jour:
        return "Aucune séance trouvée pour cette période."

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""
Tu es un coach sportif expert en musculation.

Historique complet :
{resume_historique}

Séance analysée :
{resume_jour}

Analyse cette séance et dis moi :
- Ma progression sur chaque exercice
- Les charges et reps recommandées pour la prochaine fois
- Les points à améliorer
- Un conseil général

Sois précis, concis et bienveillant.
            """
        }]
    )
    return response.choices[0].message.content

def generer_prochaine_seance(analyse: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""
Sur la base de cette analyse :
{analyse}

Génère un programme pour ma prochaine séance en JSON valide uniquement, sans texte autour :
{{
    "date_recommandee": "dans X jours",
    "exercices": [
        {{
            "nom": "Bench Press",
            "series": 4,
            "reps": 10,
            "charge_kg": 80,
            "note": "augmente de 2.5kg si tu complètes toutes les séries"
        }}
    ],
    "conseil_global": "..."
}}
            """
        }]
    )

    programme = response.choices[0].message.content

    try:
        requests.post("http://192.168.1.18:5001/save_file", json={
            "nom": "prochaine_seance.json",
            "contenu": programme
        }, timeout=5)
        print("Programme envoyé sur le PC fixe !")
    except:
        print("PC fixe injoignable, sauvegarde locale")
        with open("prochaine_seance.json", "w") as f:
            f.write(programme)

    return programme

def gerer_taches(params, device):
    type_action = params.get("type")

    if type_action == "add":
        titre = params.get("titre")
        date = params.get("date")
        result = ajouter_tache(titre, date)
        print(f"Notion response : {result}")  # debug
        if result.get("object") == "page":
            parler("Tâche ajoutée avec succès, Quentin.", device)
        else:
            parler("Erreur lors de l'ajout de la tâche.", device)

    elif type_action in ["list", "resume"]:
        taches = lister_taches()
        liste = []
        for t in taches.get("results", []):
            try:
                nom = t["properties"]["Task name"]["title"][0]["text"]["content"]
                statut = t["properties"]["Status"]["status"]["name"]
                liste.append(f"{nom} ({statut})")
            except:
                pass

        texte_taches = "\n".join(liste) if liste else "Aucune tâche trouvée"

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
        parler(response.choices[0].message.content, device)

    elif type_action == "delete":
        supprimer_tache(params.get("id"))
        parler("Tâche supprimée, Quentin.", device)


# -----------------------------
# PROGRAMME PRINCIPAL
# -----------------------------

mode = input("Mode (ecrit/oral) : ")

if mode == "ecrit":
    message = input("Votre requête : ")
    if message:
        result = ask_nova(message)
        print(result)
        device = result.get("device", DEVICE)
        action = result["action"]
        reponse = result.get("reponse", "")

        if action == "analyse_seance":
            periode = result.get("params", {}).get("periode", "last")
            parler("J'analyse ta séance, ça arrive !",device)

            # Analyse complète
            analyse = analyser_seances(periode=periode)
            print(analyse)

            # Envoie le récap écrit sur le PC fixe
            try:
                requests.post("http://192.168.1.18:5001/save_file", json={
                    "nom": "recap_seance.txt",
                    "contenu": analyse
                }, timeout=5)
            except:
                pass

            # Génère la prochaine séance
            generer_prochaine_seance(analyse)

            # Résumé oral court
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": f"""
        Sur la base de cette analyse :
        {analyse}

        Fais un résumé TRÈS court en 2-3 phrases max pour être lu à voix haute.
        Mentionne juste les points clés et la principale recommandation.
                    """
                }]
            )
            resume_oral = response.choices[0].message.content
            parler(resume_oral,device)
        elif action == "dire_heure":
            heure = datetime.now().strftime("%H:%M")
            parler(f"Il est {heure}",device)

        elif action == "gestion_taches":
            gerer_taches(result.get("params", {}), device)

        else:
            send_to_device(device, result)
            parler(reponse,device)




else:
    while True:
        message = ecouter()
        if message and "nova" in message.lower():
            commande = message.lower().replace("nova", "").strip()
            if commande:
                result = ask_nova(commande)
                print(result)
                device = result.get("device", DEVICE)
                action = result["action"]
                reponse = result.get("reponse", "")

                if action == "analyse_seance":
                    periode = result.get("params", {}).get("periode", "last")
                    parler("J'analyse ta séance, ça arrive !",device)

                    # Analyse complète
                    analyse = analyser_seances(periode=periode)
                    print(analyse)

                    # Envoie le récap écrit sur le PC fixe
                    try:
                        requests.post("http://192.168.1.18:5001/save_file", json={
                            "nom": "recap_seance.txt",
                            "contenu": analyse
                        }, timeout=5)
                    except:
                        pass

                    # Génère la prochaine séance
                    generer_prochaine_seance(analyse)

                    # Résumé oral court
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{
                            "role": "user",
                            "content": f"""
                Sur la base de cette analyse :
                {analyse}

                Fais un résumé TRÈS court en 2-3 phrases max pour être lu à voix haute.
                Mentionne juste les points clés et la principale recommandation.
                            """
                        }]
                    )
                    resume_oral = response.choices[0].message.content
                    parler(resume_oral,device)
                elif action == "dire_heure":
                    heure = datetime.now().strftime("%H:%M")
                    parler(f"Il est {heure}")
                else:
                    send_to_device(device, result)
                    parler(reponse,device)