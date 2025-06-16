import os
import time
import json
import threading
import requests
from dotenv import load_dotenv
load_dotenv()

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
INTERVAL = int(os.getenv('INTERVAL', '300'))

CONSOLES = [
    {
        "url": os.getenv('S1_CONSOLE_1'),
        "token": os.getenv('S1_TOKEN_1'),
        "seen_file": "data/seen_ids_1.json"
    },
    {
        "url": os.getenv('S1_CONSOLE_2'),
        "token": os.getenv('S1_TOKEN_2'),
        "seen_file": "data/seen_ids_2.json"
    },
    {
        "url": os.getenv('S1_CONSOLE_3'),
        "token": os.getenv('S1_TOKEN_3'),
        "seen_file": "data/seen_ids_3.json"
    }
]


# --------------------- Persistencia ---------------------

def load_seen_ids(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_ids(filename, seen_ids):
    with open(filename, "w") as f:
        json.dump(list(seen_ids), f)

# --------------------- API SentinelOne ---------------------


def get_alerts(console_url, token):
    headers = {
        'Authorization': f'ApiToken {token}',
        'Content-Type': 'application/json'
    }
    url = f"{console_url}/web/api/v2.1/threats"
    params = {
        "limit": 10,
        "sortBy": "createdAt",
        "sortOrder": "desc"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        print(f"❌ Error en {console_url}: {e}", flush=True)
        return []

# --------------------- Discord ---------------------


def send_to_discord(threat):
    sitio = threat.get("agentRealtimeInfo", "Unknown Host").get(
        "siteName", "Unknown Site")
    cliente = threat.get("agentRealtimeInfo", "Unknown Host").get(
        "accountName", "Unknown Client")
    if cliente == "CLM SOFTWARE COMERCIO,IMPORTACAO E EXPORTACAO LTDA":
        if sitio == "CO_VENTURA SYSTEMS - ANTIOQUIA GOLD":
            cliente = "Antioquiagold"
        else:
            return
    hostname = threat.get("agentRealtimeInfo", "Unknown Host").get(
        "agentComputerName", "Unknown Host")
    threat_name = threat.get("threatInfo", "Unknown Threat").get(
        "threatName", "Unknown Threat")
    threat_originator = threat.get("threatInfo", "Unknown Threat").get(
        "originatorProcess", "Unknown Originator")
    threat_classification = threat.get("threatInfo", "Unknown Threat").get(
        "classification", "Unknown Classification")
    threat_confidence_level = threat.get(
        "threatInfo", "Unknown Threat").get("confidenceLevel", "N/A")

    message = (
        f"🚨 **Alerta SentinelOne**\n"
        f"💼 **Cliente:** {cliente}\n"
        f"🖥️ Host: `{hostname}`\n"
        f"🦠 Amenaza: `{threat_name}`\n"
        f"🔍 Proceso Originador: `{threat_originator}`\n"
        f"📊 Clasificación: `{threat_classification}`\n"
        f"🔒 Confianza: `{threat_confidence_level}`"
    )

    requests.post(DISCORD_WEBHOOK, json={"content": message})


def loop_consola(console_url, token, seen_file):
    print(
        f"📡 Monitoreando {console_url} cada {INTERVAL} segundos...", flush=True)
    seen_ids = load_seen_ids(seen_file)

    while True:
        alerts = get_alerts(console_url, token)
        nuevos = False
        for alert in alerts:
            if alert['id'] not in seen_ids and alert.get("threatInfo", {}).get("incidentStatus") == "unresolved":
                send_to_discord(alert)
                seen_ids.add(alert['id'])
                nuevos = True
        if nuevos:
            save_seen_ids(seen_file, seen_ids)
        time.sleep(INTERVAL)

# --------------------- Main Loop ---------------------


def main():
    threads = []
    for config in CONSOLES:
        t = threading.Thread(target=loop_consola, args=(
            config["url"], config["token"], config["seen_file"]))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
