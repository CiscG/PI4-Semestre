import express from "express";
import fs from "fs-extra";
import cors from "cors";

const app = express();
const PORT = 3000; // 🔹 Porta do backend
const DB_FILE = "./data.json";

app.use(cors());
app.use(express.json());

// Garante que o arquivo data.json exista
if (!fs.existsSync(DB_FILE)) fs.writeJsonSync(DB_FILE, []);

// 🔸 Rota para receber dados do sensor
app.post("/api/peso", async (req, res) => {
  const data = req.body;

  if (!data.device_id || !data.weight)
    return res.status(400).json({ error: "Campos inválidos." });

  const entry = {
    device_id: data.device_id,
    weight: data.weight,
    timestamp: new Date().toISOString()
  };

  const allData = await fs.readJson(DB_FILE);
  allData.push(entry);
  await fs.writeJson(DB_FILE, allData, { spaces: 2 });

  console.log("📥 Dado recebido:", entry);
  res.json({ message: "Dado salvo com sucesso!", entry });
});

// 🔸 Rota para consultar dados
app.get("/api/peso", async (req, res) => {
  const allData = await fs.readJson(DB_FILE);
  res.json(allData);
});

app.listen(PORT, () => {
  console.log(`🚀 Servidor rodando em http://localhost:${PORT}`);
});
