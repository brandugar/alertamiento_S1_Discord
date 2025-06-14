import os
import time
import json
import requests
from dotenv import load_dotenv
load_dotenv()

S1_TOKEN = os.getenv('S1_TOKEN_2')
S1_CONSOLE = os.getenv('S1_CONSOLE_2')  # sin / al final
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
INTERVAL = int(os.getenv('INTERVAL', '300'))
SEEN_FILE = "data/seen_ids.json"

HEADERS = {
    'Authorization': f'ApiToken {S1_TOKEN}',
    'Content-Type': 'application/json'
}

# --------------------- Persistencia ---------------------


def load_seen_ids():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_ids(seen_ids):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_ids), f)

# --------------------- API SentinelOne ---------------------


def get_alerts():
    url = f"{S1_CONSOLE}/web/api/v2.1/threats"
    params = {
        "limit": 10,
        "sortBy": "createdAt",
        "sortOrder": "desc"
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        print(f"❌ Error al obtener alertas: {e}")
        return []

# --------------------- Discord ---------------------


def send_to_discord(threat):
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
        f"🖥️ Host: `{hostname}`\n"
        f"🦠 Amenaza: `{threat_name}`\n"
        f"🔍 Proceso Originador: `{threat_originator}`\n"
        f"📊 Clasificación: `{threat_classification}`\n"
        f"🔒 Confianza: `{threat_confidence_level}`"
    )

    requests.post(DISCORD_WEBHOOK, json={"content": message})

# --------------------- Main Loop ---------------------


def main():
    print(
        f"📡 Monitoreando SentinelOne cada {INTERVAL} segundos...")
    seen_ids = load_seen_ids()

    while True:
        alerts = get_alerts()
        new_ids = False
        for alert in alerts:
            if alert['id'] not in seen_ids and alert.get("threatInfo", {}).get("incidentStatus", "desconocido") == "unresolved":
                send_to_discord(alert)
                seen_ids.add(alert['id'])
                new_ids = True
        if new_ids:
            save_seen_ids(seen_ids)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
