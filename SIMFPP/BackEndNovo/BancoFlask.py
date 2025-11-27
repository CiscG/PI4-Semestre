# app.py
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
import MySQLdb
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------- CONFIGURE AQUI ----------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'simfpp_user'   # ou 'root'
app.config['MYSQL_PASSWORD'] = 'SUA_SENHA'
app.config['MYSQL_DB'] = 'simfpp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# ------------------------------------

mysql = MySQL(app)

def criar_banco_e_tabela():
    try:
        # conecta sem banco primeiro para garantir criação
        conn = MySQLdb.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            passwd=app.config['MYSQL_PASSWORD']
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS simfpp")
        cursor.close()
        conn.close()

        # agora cria tabela caso não exista
        conn = MySQLdb.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            passwd=app.config['MYSQL_PASSWORD'],
            db='simfpp'
        )
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
        print("✅ Banco e tabela verificados/criados com sucesso!")
    except Exception as e:
        print("❌ Erro ao criar banco/tabela:", e)

# cria tudo ao iniciar
criar_banco_e_tabela()

# --------- ENDPOINTS ----------
@app.route("/api/weight", methods=["POST"])
def receber_peso():
    try:
        data = request.get_json(force=True)
        grams = data.get("grams")
        timestamp = data.get("timestamp")  # espera string ISO

        if grams is None or timestamp is None:
            return jsonify({"erro": "Dados inválidos"}), 400

        # converte timestamp para datetime
        try:
            ts_dt = datetime.fromisoformat(timestamp)
        except Exception:
            # se não for ISO, tenta interpretar como inteiro ms desde epoch
            try:
                ms = int(timestamp)
                ts_dt = datetime.fromtimestamp(ms/1000.0)
            except Exception:
                return jsonify({"erro": "timestamp inválido"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO readings (grams, timestamp)
            VALUES (%s, %s)
        """, (float(grams), ts_dt))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"status": "OK", "grams": grams, "timestamp": ts_dt.isoformat()})
    except Exception as e:
        return jsonify({"status":"ERRO","mensagem": str(e)}), 500

@app.route("/api/readings", methods=["GET"])
def listar_leituras():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, grams, timestamp, created_at FROM readings ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    cursor.close()
    return jsonify(rows)

@app.route("/")
def home():
    return "✅ API SimFPP funcionando!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
