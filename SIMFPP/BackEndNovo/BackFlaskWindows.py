from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app)

# -------- CONFIG MYSQL --------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",      # altere se necessário
    "password": "",     # coloque sua senha se tiver
    "database": "simfpp"
}
# -----------------------------

# ---------- CRIA BANCO E TABELA ----------
def criar_banco_e_tabela():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS simfpp")
        cursor.close()
        conn.close()

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                grams FLOAT NOT NULL,
                timestamp DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Banco e tabela criados/verificados com sucesso!")

    except Exception as e:
        print("❌ Erro ao criar banco/tabela:", e)

criar_banco_e_tabela()

# ---------- ENDPOINT PARA RECEBER PESO ----------
@app.route("/api/weight", methods=["POST"])
def receber_peso():
    try:
        data = request.get_json(force=True)

        grams = data.get("grams")
        timestamp = data.get("timestamp")

        if grams is None or timestamp is None:
            return jsonify({"status": "ERRO", "mensagem": "Dados inválidos"}), 400

        timestamp_dt = datetime.fromisoformat(timestamp)

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO readings (grams, timestamp)
            VALUES (%s, %s)
        """, (float(grams), timestamp_dt))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "OK",
            "grams": grams,
            "timestamp": timestamp
        })

    except Exception as e:
        return jsonify({"status": "ERRO", "mensagem": str(e)}), 500

# ---------- ENDPOINT PARA O SITE ----------
@app.route("/api/readings", methods=["GET"])
def listar_leituras():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT grams, timestamp FROM readings ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(rows)

@app.route("/")
def home():
    return "✅ API SimFPP funcionando com MySQL!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
