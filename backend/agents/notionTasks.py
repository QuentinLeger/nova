import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from groq.types.chat import ChatCompletionUserMessageParam
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

load_dotenv()

def get_headers():
    load_dotenv()
    return {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def ajouter_tache(titre, date=None):
    data = {
        "parent": {"database_id": os.getenv("NOTION_DATABASE_ID")},
        "properties": {
            "Task name": {"title": [{"text": {"content": titre}}]},
            "Status": {"status": {"name": "Not started"}}
        }
    }
    if date:
        data["properties"]["Due date"] = {"date": {"start": date}}
    r = requests.post("https://api.notion.com/v1/pages", headers=get_headers(), json=data)
    return r.json()

def lister_taches():
    r = requests.post(
        f"https://api.notion.com/v1/databases/{os.getenv('NOTION_DATABASE_ID')}/query",
        headers=get_headers()
    )
    return r.json()

def supprimer_tache(page_id):
    r = requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=get_headers(),
        json={"archived": True}
    )
    return r.json()




#####
def gerer_taches(params, device,parler):
    type_action = params.get("type")

    if type_action == "add":
        titre = params.get("titre")
        date = params.get("date")

        if date == "demain":
            date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif date in ["aujourd'hui", "aujourd hui"]:
            date = datetime.now().strftime("%Y-%m-%d")
        elif date == "après-demain":
            date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

        result = ajouter_tache(titre, date)
        if result.get("object") == "page":
            parler(f"Votre tâche a été ajoutée, Quentin.", device)
        else:
            parler(f"Erreur lors de l'ajout, Quentin.", device)

    elif type_action in ["list", "resume"]:
        date_filtre = params.get("date")
        taches = lister_taches()
        liste = []
        for t in taches.get("results", []):
            try:
                nom = t["properties"]["Task name"]["title"][0]["text"]["content"]
                statut = t["properties"]["Status"]["status"]["name"]
                if date_filtre:
                    due = t["properties"].get("Due date", {}).get("date")
                    if due and due.get("start") == date_filtre:
                        liste.append(f"{nom} ({statut})")
                else:
                    liste.append(f"{nom} ({statut})")
            except:
                pass

        texte_taches = "\n".join(liste) if liste else "Aucune tâche trouvée"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[ChatCompletionUserMessageParam(role="user", content=f"""
                Tu es Nova, l'assistante vocale de Quentin.
                Résume ces tâches à l'oral en 2-3 phrases max, en français, de façon naturelle et chaleureuse.
                Mets en avant les tâches urgentes ou proches si il y en a.
                Utilise "vous" pour t'adresser à Quentin.
                N'utilise pas d'apostrophes contractées (J' → Je, etc.)

                Tâches :
                {texte_taches}
            """)]
        )
        parler(response.choices[0].message.content, device)

    elif type_action == "delete":
        supprimer_tache(params.get("id"))
        parler("Tâche supprimée, Quentin.", device)

##### partie gestion de taches
