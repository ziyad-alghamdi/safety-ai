// server.js
const io = require('socket.io')(4000, {
  cors: { origin: "*" } 
});

io.on('connection', (socket) => {
  console.log('✅ New connection established'); // بدلاً من العربي

  socket.on('update_data', (data) => {
    console.log('📊 Data received:', data); // بدلاً من العربي
    io.emit('display_data', data); 
  });
});

console.log('🚀 Socket server running on port 4000');