from .system import ouvrir_site



##    "ouvrir_app": ouvrir_app,"dire_heure": dire_heure,"macro": macro, "controle_domotique": controle_domotique, "gestion_taches": gestion_taches,


ACTION_HANDLERS = {
    "ouvrir_site": ouvrir_site,

}

def execute_action(result : dict):
    action = result.get("action")
    handler = ACTION_HANDLERS.get(action)
    if handler is None:
        return None
    return handler(result.get("params",{}), result.get("device","pc_fixe"))