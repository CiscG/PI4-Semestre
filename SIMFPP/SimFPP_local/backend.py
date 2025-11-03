# backend.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import threading
import os
from typing import List

DATA_FILE = "data.json"

app = FastAPI(title="SimFPP Local Backend (JSON)")

# permite chamadas do browser local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class WeightItem(BaseModel):
    grams: float
    timestamp: str  # ISO format

def read_store() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def write_store(items: List[dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

@app.on_event("startup")
def ensure_store():
    if not os.path.exists(DATA_FILE):
        write_store([])

@app.post("/api/weight", status_code=201)
def post_weight(item: WeightItem):
    items = read_store()
    items.append({"id": int(datetime.utcnow().timestamp() * 1000),
                  "grams": item.grams,
                  "timestamp": item.timestamp})
    write_store(items)
    return {"status": "ok", "saved": items[-1]}

@app.get("/api/readings")
def get_readings(limit: int = 100):
    items = read_store()
    # ordena por timestamp asc
    items_sorted = sorted(items, key=lambda x: x["timestamp"])
    if limit:
        items_sorted = items_sorted[-limit:]
    return items_sorted

@app.get("/api/last")
def get_last():
    items = read_store()
    if not items:
        raise HTTPException(status_code=404, detail="No readings")
    last = max(items, key=lambda x: x["timestamp"])
    return last

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
