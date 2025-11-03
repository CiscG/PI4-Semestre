from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import sqlite3


app = FastAPI(title="SimFPP - Backend Local")


DB = "database.db"


# Inicializa o banco
def init_db():
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS readings (
id INTEGER PRIMARY KEY AUTOINCREMENT,
timestamp TEXT,
grams REAL
)''')
conn.commit()
conn.close()


init_db()


class WeightData(BaseModel):
grams: float
timestamp: str


@app.post("/api/weight")
def receive_weight(data: WeightData):
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("INSERT INTO readings (timestamp, grams) VALUES (?, ?)", (data.timestamp, data.grams))
conn.commit()
conn.close()
return {"message": "Weight recorded", "grams": data.grams}


@app.get("/api/readings")
def get_readings():
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 50")
rows = c.fetchall()
conn.close()
return [{"id": r[0], "timestamp": r[1], "grams": r[2]} for r in rows]


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