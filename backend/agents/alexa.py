import asyncio
import os
from alexapy import AlexaLogin, AlexaAPI

email_compte = "atomiccreeperboss@gmail.com"


async def obtenir_tous_les_appareils(alexa_key):
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

    print("[ALEXA] Tentative de connexion...")
    await login.login()

    # --- Vérification du statut de connexion ---
    if login.status != "LOGIN":
        print(f"\n[🚨 SÉCURITÉ AMAZON] Statut : {login.status}")

        # Si Amazon demande une action (Captcha, validation OTP)
        if login.url:
            print(f"👉 Ouvre urgemment cette URL dans ton navigateur pour valider :")
            print(f"   {login.url}\n")

        # On attend 30 secondes pour te laisser le temps de valider sur ton navigateur/téléphone
        print("[ALEXA] Pause de 30 secondes pour te laisser valider la sécurité d'Amazon...")
        await asyncio.sleep(30)

        # On tente de finaliser la session après la pause
        await login.login()

    # Si c'est validé (ou si on tente le coup), on instancie l'API
    try:
        api = AlexaAPI(device="ProjetJarvis", login=login)
        raw_devices = await api.get_devices(login=login)

        # Fermeture propre de la session pour éviter les alertes "Unclosed client session"
        await login.close()

        if raw_devices:
            noms_appareils = [d.get("accountName") for d in raw_devices if d.get("accountName")]
            print(f"Appareils Alexa trouvés : {noms_appareils}")
            return noms_appareils
        else:
            print("[ALEXA] Aucun appareil renvoyé ou reconnexion nécessaire.")
            return ["Aucun appareil trouvé"]

    except Exception as e:
        print(f"[ALEXA ERROR] Échec de la récupération : {e}")
        await login.close()
        return [f"Erreur API : {e}"]