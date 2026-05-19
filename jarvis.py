from flask import Flask, request
import subprocess
import webbrowser
import json
import datetime

app = Flask(__name__)

with open("config.json") as f:
    CONFIG = json.load(f)

def executer_action(data):
    action = data["action"]

    if action == "ouvrir_site":
        webbrowser.open(data["params"]["url"])

    elif action == "dire_heure":
        heure = datetime.datetime.now().strftime("%H:%M")
        print(f"Il est {heure}")

    elif action == "repondre":
        print(data["params"].get("reponse", ""))

    elif action == "ouvrir_app":
        app_name = data["params"]["app"]
        app_path = CONFIG["apps"].get(app_name)
        if app_path:
            subprocess.Popen(app_path)
        else:
            print(f"App inconnue : {app_name}")

    elif action == "macro":
        nom = data["params"]["nom"]
        macro = CONFIG["macros"].get(nom)
        if macro:
            for commande in macro:
                executer_action(commande)
        else:
            print(f"Macro inconnue : {nom}")


@app.post("/execute")
def execute():
    executer_action(request.json)
    return {"status": "ok"}

app.run(host="0.0.0.0", port=5001)