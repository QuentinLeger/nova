from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("api_key")
client = Groq(api_key=api_key)

def ask_nova(message: str):
    prompt = f"{message}"

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",  # Copié direct de ta liste API
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
