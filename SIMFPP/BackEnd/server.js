import { fastify } from 'fastify'
import { DatabaseMemory } from './database-memory.js'

const server = fastify()

const database = new DatabaseMemory()

//GET, busco informação
//POST, criação https://localhost:3333/videos
//PUT, alteração https://localhost:3333/video/3
//DELETE, https://localhost:3333/video/3
//PATCH, altera pequenos ddados
//Route Parameter


server.post('/videos', (request, reply) =>{
   const { title, description, duration } = request.body

   //console.log(body)

   database.create({
      title,
      description,
      duration,
   })
   console.log(database.list())
   
   return reply.status(201).send()
})

server.get('/videos', (request, reply) =>{
   const videos = database.list()

   console.log(videos)
   
   return videos
   
   //return 'Hello Rocketseat'
})

server.put('/videos/:id', () => {
   return 'Hello Node.js'
})
server.delete('/videos/:id', () => {
   return 'Hello Node.js'
})

server.get('/', () => {
   return 'Hello World'
})
server.get('/hello', () => {
   return 'Hello Chico'
})
server.get('/node', () => {
   return 'Hello Node.js'
})

server.listen({
   port:3333,
})