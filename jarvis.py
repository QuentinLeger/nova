from flask import Flask, request
import subprocess
import webbrowser
import json
import datetime

app = Flask(__name__)

with open("config_pc_fixe.json") as f:
    CONFIG = json.load(f)

@app.post("/execute")
def execute():
    data = request.json
    action = data["action"]

    if action == "ouvrir_site":
        webbrowser.open(data["params"]["url"])

    elif action == "dire_heure":
        heure = datetime.datetime.now().strftime("%H:%M")
        print(f"Il est {heure}")

    elif action == "repondre":
        print(data["params"]["reponse"])

    elif action == "ouvrir_app":
        app_name = data["params"]["app"]
        app_path = CONFIG["apps"].get(app_name)

        if app_path:
            subprocess.call(app_path)
        else:
            print(f"App inconnue : {app_name}")

    return {"status": "ok"}

app.run(host="0.0.0.0", port=5001)
