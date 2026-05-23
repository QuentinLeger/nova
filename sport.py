import base64
import os
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
DEVICE = "pc_fixe"

def analyser_screenshots():
    images = []
    dossier = "C:/seances/"  # dossier où tu mets tes screens

    for fichier in os.listdir(dossier):
        if fichier.endswith(".png") or fichier.endswith(".jpg"):
            with open(f"{dossier}/{fichier}", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                images.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"}
                })

    response = client.chat.completions.create(
        model="llama-4-scout-17b-16e-instruct",  # modèle vision Groq
        messages=[{
            "role": "user",
            "content": images + [
                {"type": "text", "text": "Analyse ma séance et donne moi les recommandations pour la prochaine fois"}]
        }]
    )
    return response.choices[0].message.content