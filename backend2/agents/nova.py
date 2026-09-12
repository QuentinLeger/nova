from groq import Groq
from dotenv import load_dotenv
import json
import requests
import os

load_dotenv()
api_key = os.getenv("api_key")
client = Groq(api_key=api_key)


def ask_nova(message: str):
    prompt =f"{message}"


    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    print(response)