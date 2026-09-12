import webbrowser
from datetime import datetime

def ouvrir_site(params : dict, device: str):
    url = params.get("url")
    if url:
        webbrowser.open(url)