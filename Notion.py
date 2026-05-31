import requests
import os
from dotenv import load_dotenv

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