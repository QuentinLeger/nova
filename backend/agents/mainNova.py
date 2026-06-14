import json
import requests
import os
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from sport import analyser_seances, generer_prochaine_seance
from notionTasks import gerer_taches
from audio import parler, ecouter

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
DEVICE = "pc_fixe"



### Principal prompt for NOVA
def ask_nova(message: str):
    prompt = f"""
    Tu es Nova. Réponds UNIQUEMENT en JSON valide.
    Tu réponds TOUJOURS en français, peu importe la langue de la question.
    Toutes tes réponses dans le champ "reponse" sont en français.

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
    - "Voilà qui est fait Quentin. Autre chose ?"
    - "Je lance ça pour vous Quentin !"
    Tes réponses doivent être naturelles et fluides à l'oral.
    Utilise des virgules pour créer des pauses naturelles.
    Exemple : "Bien sur, je vous lance Steam pour vous Quentin. " et réponse personalisé genre voulez vous jouer etc ? 
    Plutôt que : "J'ouvre Steam dès maintenant."
    Tu t'appelles Nova, tu es l'assistante de Quentin.
    Tu es professionnelle, efficace, avec une légère touche d'humour.
    
    Pour les dates dans gestion_taches, toujours utiliser le format ISO : YYYY-MM-DD
    Exemple : "demain" → "2026-06-01", "aujourd'hui" → "2026-05-31"
    La date d'aujourd'hui est {datetime.now().strftime("%Y-%m-%d")}

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

### End of prompt



### Send to a device
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




def executer(result):
    device = result.get("device", DEVICE)
    action = result.get("action", "")
    reponse = result.get("reponse", "")

    if action == "analyse_seance":
        periode = result.get("params", {}).get("periode", "last")
        parler("Je lance l'analyse de ta séance, ça arrive !", device)
        analyse = analyser_seances(periode=periode)
        generer_prochaine_seance(analyse)
        parler(analyse, device)  # ← direct, sans résumé

    elif action == "dire_heure":
        parler(f"Il est {datetime.now().strftime('%H:%M')}",device)

    elif action == "gestion_taches":
        gerer_taches(result.get("params", {}),device)


    else :
        send_to_device(device,result)
        parler(result["reponse"],device)


# -----------------------------
# PROGRAMME PRINCIPAL
# -----------------------------

mode = input("Mode (ecrit/oral) : ")

if mode == "ecrit":
    message = input("Votre requête : ")
    if message:
        result = ask_nova(message)
        print(result)
        executer(result)

else:
    while True:
        message = ecouter()
        if message and "nova" in message.lower():
            commande = message.lower().replace("nova", "").strip()
            if commande:
                result = ask_nova(commande)
                print(result)
                executer(result)
