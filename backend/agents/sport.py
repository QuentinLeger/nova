import os
import pandas as pd
from datetime import datetime, timedelta
from groq import Groq
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def analyser_seances(periode="today"):
    df = pd.read_csv("../../workouts.csv")
    df['start_time'] = pd.to_datetime(df['start_time'], format="%b %d, %Y, %I:%M %p")

    aujourd_hui = datetime.now().date()

    if periode == "today":
        df_filtre = df[df['start_time'].dt.date == aujourd_hui]
    elif periode == "week":
        debut_semaine = aujourd_hui - timedelta(days=7)
        df_filtre = df[df['start_time'].dt.date >= debut_semaine]
    elif periode == "last":  # ajoute ça
        df_filtre = df[df['start_time'] == df['start_time'].max()]
    else:
        df_filtre = df

    # Historique complet
    resume_historique = ""
    for (date, exercice), groupe in df.groupby(['start_time', 'exercise_title']):
        series = ", ".join([f"{r['weight_kg']}kg x{int(r['reps'])}" for _, r in groupe.iterrows()])
        resume_historique += f"{date} - {exercice}: {series}\n"

    # Séance filtrée
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

Historique complet de mes séances :
{resume_historique}

Séance analysée :
{resume_jour}

Analyse cette séance par rapport à mon historique et dis moi :
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

Génère un programme pour ma prochaine séance en JSON valide :
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

    print("Programme sauvegardé dans prochaine_seance.json")
    return programme
