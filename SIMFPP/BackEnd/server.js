// import { fastify } from 'fastify'
// import { DatabaseMemory } from './database-memory.js'

// const server = fastify()

// const database = new DatabaseMemory()

// //GET, busco informação
// //POST, criação https://localhost:3333/videos
// //PUT, alteração https://localhost:3333/video/3
// //DELETE, https://localhost:3333/video/3
// //PATCH, altera pequenos ddados
// //Route Parameter


// server.post('/videos', (request, reply) =>{
//    const { title, description, duration } = request.body

//    //console.log(body)

//    database.create({
//       title,
//       description,
//       duration,
//    })
//    console.log(database.list())
   
//    return reply.status(201).send()
// })

// server.get('/videos', (request, reply) =>{
//    const videos = database.list()

//    console.log(videos)
   
//    return videos
   
//    //return 'Hello Rocketseat'
// })

// server.put('/videos/:id', (request, reply) => {
//    const videoId = request.params.id
//    const { title, description, duration } = request.body

//    database.update(videoId,{
//       title,
//       description,
//       duration,
//    })
   
//    return reply.status(204).send()

//    //return 'Hello Node.js'
// })
// server.delete('/videos/:id', (request, reply) => {
//    const videoId = request.params.id
   
//    database.delete(videoId)

//    return reply.status(204).send()
   
//    //return 'Hello Node.js'
// })

// server.get('/', () => {
//    return 'Hello World'
// })
// server.get('/hello', () => {
//    return 'Hello Chico'
// })
// server.get('/node', () => {
//    return 'Hello Node.js'
// })

// server.listen({
//    port:3333,
// })

const express = require('express');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');

const DATA_FILE = path.join(__dirname, 'data.json');
const PORT = process.env.PORT || 3000;
const MAX_HISTORY = 10000; //verificar valores

const app = express();
app.use(bodyParser.json());

//habilita CORS simples
app.use((req, res, next) => {
   res.header('Access-Control-Allow-Origin', '*');
   res.header('Access-Control-Allow-Origin', 'Content-Type');
   next();
});

//garante arquivo
if (!fs.existsSync(DATA_FILE)) {
   fs.writeFileSync(DATA_FILE, JSON.stringify({ readings: []}, null, 2));
}

//carrega em memoria
let DB = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));

function persistDB() {
   try {
      fs.writeFileSync(DATE_FILE, JSON.stringify(DB, null, 2), 'uft8');
   } catch (err) {
      console.error('Erro ao salvar data.json:', err);
   }
}

//POST /data -> recebe leitura com formato C: { id: string, dados: (peso: number, horario: string)}
app.post('/data', (req, res) => {
   const payload = req.body;
   if (!payload || !payload.id || payload.dados || typeof payload.dados.peso === 'undefined' || !payload.dados.horario){
      return res.status(400).json({error: 'Payload invalido. Esperando: {id, dados: { peso, horario } }'});
   }
   
})