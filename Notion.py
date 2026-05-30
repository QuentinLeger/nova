import requests
import os

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def ajouter_tache(titre, date=None):
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": titre}}]},
            "Status": {"status": {"name": "À faire"}}
        }
    }
    if date:
        data["properties"]["Date"] = {"date": {"start": date}}

    r = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    return r.json()

def lister_taches():
    r = requests.post(
        f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
        headers=headers
    )
    return r.json()

def supprimer_tache(page_id):
    r = requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"archived": True}
    )
    return r.json()
