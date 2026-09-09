import asyncio
import os
from alexapy import AlexaLogin, AlexaAPI

email_compte = "atomiccreeperboss@gmail.com"


# La fonction accepte désormais la clé en argument
async def obtenir_tous_les_appareils(alexa_key):
    # Petit check de sécurité
    if not alexa_key:
        print("[ALEXA ERROR] Le serveur central n'a pas transmis la clé ALEXA_KEY !")
        return ["Erreur clé absente"]

    dossier_actuel = os.path.dirname(os.path.abspath(__file__))

    login = AlexaLogin(
        url="amazon.fr",
        email=email_compte,
        password=alexa_key,
        outputpath=dossier_actuel
    )

    login._hass_domain = "alexapy"

    print("[ALEXA] Tentative de connexion après réparation de la lib...")
    await login.login()

    api = AlexaAPI(login)
    raw_devices = await api.get_devices()

    noms_appareils = [d.get("accountName") for d in raw_devices if d.get("accountName")]
    print(f"Appareils Alexa trouvés : {noms_appareils}")
    return noms_appareils