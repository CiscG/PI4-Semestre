# sensor.py
import time
import random
import requests
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000/api/weight"
INTERVAL_SECONDS = 5

def simulate_reading():
    # Simula variação de peso no pote (em gramas)
    # ajuste a faixa conforme quiser
    return round(random.uniform(5.0, 60.0), 2)

def send_reading(grams):
    payload = {
        "grams": grams,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        resp = requests.post(BACKEND_URL, json=payload, timeout=5)
        resp.raise_for_status()
        print(f"[OK] Sent {grams} g -> {resp.status_code}")
    except Exception as e:
        print("[ERR] Could not send reading:", e)

def main():
    print("Sensor simulator started. Sending to", BACKEND_URL)
    while True:
        grams = simulate_reading()
        send_reading(grams)
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
