import base64
import os
from groq import Groq
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
DEVICE = "pc_fixe"



def analyser_seances(periode="today"):
    df = pd.read_csv("workouts.csv")
    df['start_time'] = pd.to_datetime(df['start_time'], format="%b %d, %Y, %I:%M %p")

    # Filtre selon la période demandée
    aujourd_hui = datetime.now().date()

    if periode == "today":
        df_filtre = df[df['start_time'].dt.date == aujourd_hui]
    elif periode == "week":
        debut_semaine = aujourd_hui - timedelta(days=7)
        df_filtre = df[df['start_time'].dt.date >= debut_semaine]

    # Historique complet pour contexte
    resume_historique = df.groupby(['start_time', 'exercise_title']).apply(
        lambda x: f"{x['exercise_title'].iloc[0]}: " +
                  ", ".join([f"{r['weight_kg']}kg x{r['reps']}" for _, r in x.iterrows()])
    ).to_string()

    # Séance du jour
    resume_jour = df_filtre.groupby(['exercise_title']).apply(
        lambda x: f"{x['exercise_title'].iloc[0]}: " +
                  ", ".join([f"{r['weight_kg']}kg x{r['reps']}" for _, r in x.iterrows()])
    ).to_string()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""
            Historique complet : {resume_historique}

            Séance d'aujourd'hui : {resume_jour}

            Analyse ma séance d'aujourd'hui par rapport à mon historique et dis moi :
            - Ma progression sur chaque exercice
            - Les charges/reps recommandées pour la prochaine fois
            - Les points à améliorer
            Sois précis et concis.
            """
        }]
    )
    return response.choices[0].message.content

print(analyser_seances(periode="today"))