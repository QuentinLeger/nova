from groq import Groq
import json
import datetime
import webbrowser
import subprocess

client = Groq(api_key="")


def ask_jarvis(message: str):
    prompt = f"""
Tu es Jarvis. Réponds UNIQUEMENT en JSON valide.

Actions possibles :
- ouvrir_site : ouvre un site web
- dire_heure : donne l'heure actuelle  
- repondre : répond à une question normale
- ouvrir_app : ouvre une app

Précision sites : 
Quand je dis Arche c'est arche.univ-lorraine

Applications disponibles :
- steam : C:\\Program Files (x86)\\Steam\\steam.exe
- vscode : C:\\Users\\qlege\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe
- chrome : C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe
- claude : C:\\Program Files\\WindowsApps\\Claude_1.6259.1.0_x64__pzs8sxrjxfjjc\\app\\claude.exe
- deezer : C:\\Program Files\\WindowsApps\\Deezer.62021768415AF_7.1.190.0_x86__q7m17pa7q8kj0\\app\\Deezer.exe
- pycharm : C:\\Program Files\\JetBrains\\PyCharm 2026.1.1\\bin\\pycharm64.exe
- intelliJ : C:\\Program Files\\JetBrains\\IntelliJ IDEA 2025.3.4\\bin\\idea64.exe



Exemples :
{{"action": "ouvrir_site", "params": {{"url": "https://youtube.com"}}}}
{{"action": "ouvrir_app", "params": {{"app": "C:\\Program Files (x86)\\Steam\\steam.exe"}}}}

Phrase : "{message}"
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content
    return json.loads(text)


message = input("Requete : ")
result = ask_jarvis(message)
print(result)
print()
# {'action': 'ouvrir_site', 'params': {'url': 'https://youtube.com'}}

action = result["action"]
if action == "ouvrir_site":
    import webbrowser
    webbrowser.open(result["params"]["url"])

if action == "dire_heure" :
    heure = datetime.datetime.now().strftime("%H:%M")
    print(f"Il est {heure}")

if action == "repondre" :
    print(result["params"]["reponse"])

if action == "ouvrir_app":
    subprocess.call(result["params"]["app"])