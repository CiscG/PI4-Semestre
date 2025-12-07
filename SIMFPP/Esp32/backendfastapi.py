from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI(title="SimFPP - Backend Local")

# =========================
# ✅ LIBERA CORS (OBRIGATÓRIO PARA O FRONT)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Libera qualquer origem (DEV)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# BANCO DE DADOS
# =========================

DB = "database.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            grams REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# =========================
# MODELO
# =========================

class WeightData(BaseModel):
    grams: float

# =========================
# ROTAS
# =========================

@app.post("/api/weight")
def receive_weight(data: WeightData):
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO readings (timestamp, grams) VALUES (?, ?)",
        (timestamp, data.grams)
    )
    conn.commit()
    conn.close()

    return {
        "message": "Weight recorded",
        "grams": data.grams,
        "timestamp": timestamp
    }

@app.get("/api/readings")
def get_readings():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()

    return [
        {"id": r[0], "timestamp": r[1], "grams": r[2]}
        for r in rows
    ]

@app.get("/api/last")
def get_last():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT timestamp, grams FROM readings ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()

    if row:
        return {"timestamp": row[0], "grams": row[1]}

    return {"message": "No data yet"}
