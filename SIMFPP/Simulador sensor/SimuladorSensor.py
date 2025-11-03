'''import requests
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
        time.sleep(3)  # intervalo de 3 segundos entre leituras'''

import requests
import random
import time
import uuid
from datetime import datetime

#troque para a URL do seu backend (p.ex. https://meu-backend.com/data)
SERVER_URL = "https://localhost:3000/data"

#id do sensor (pode ser alterado manualmente)
SENSOR_ID = str(uuid.uuid4())[:8]

#simula diferença de peso (pode ser negativa ou positiva) e envia horario

def generate_reading():
    #diferença de peso em kg, por exemplo -0.5..+5.0
    peso = round(random.uniform(-0.5, 5.0), 3)
    #horario no formato ISO 8601
    horario = datetime.utcnow().isoformat() + 'Z'
    return{
        "id": SENSOR_ID,
        "dados":{
            "peso": peso,
            "horario": horario
        }
    }

def main():
    while True:
        reading = generate_reading()
        try:
            resp = requests.post(SERVER_URL, json=reading, timeout=5)
            print('Enviado', reading, '->', resp.status_code,resp.text)
        except Exception as e:
            print('Erro ao enviar', e)
        time.sleep(1) #ajusta intervalo conforme necessário

if __name__ == '__main__':
    main()