import requests
import random
import time
import json

URL = "http://localhost:3000/pesagens"

def gerar_peso():
    # Simula uma leitura entre 0.00 e 100.00 kg
    return round(random.uniform(0.0, 100.0), 2)

def enviar_peso(peso):
    dados = {"peso": peso}
    try:
        r = requests.post(URL, json=dados)
        if r.status_code == 200:
            print(f"✅ Peso enviado: {peso} kg")
        else:
            print(f"⚠️ Erro ao enviar: {r.status_code}")
    except Exception as e:
        print(f"❌ Falha de conexão: {e}")

if __name__ == "__main__":
    while True:
        peso = gerar_peso()
        enviar_peso(peso)
        time.sleep(3)  # intervalo de 3 segundos entre leituras