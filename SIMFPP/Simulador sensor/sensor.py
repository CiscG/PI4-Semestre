import time
import random
import requests
from datetime import datetime


BACKEND_URL = "http://127.0.0.1:8000/api/weight"


print("Simulador HX711 iniciado... Enviando leituras ao backend.")


while True:
grams = round(random.uniform(100.0, 500.0), 2) # peso aleatório
payload = {
"grams": grams,
"timestamp": datetime.now().isoformat()
}


try:
r = requests.post(BACKEND_URL, json=payload, timeout=5)
if r.status_code == 200:
print(f"[OK] {grams}g enviado.")
else:
print(f"[ERRO] {r.status_code}: {r.text}")
except Exception as e:
print(f"[FALHA] {e}")


time.sleep(5)