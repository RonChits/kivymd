const WebSocket = require('ws');
const PORT = process.env.WS_PORT || 8081;

const wss = new WebSocket.Server({ port: PORT });

let users = {}; // username -> ws

function broadcastUserList() {
  const names = Object.keys(users);
  const msg = JSON.stringify({ type: 'userlist', users: names });
  Object.values(users).forEach(ws => ws.send(msg));
}

wss.on('connection', function connection(ws) {
  let username = null;

  ws.on('message', function incoming(message) {
    try {
      const data = JSON.parse(message);
      if (data.type === 'join') {
        username = data.name;
        users[username] = ws;
        broadcastUserList();
      }
      // Forward invites, chat, game, score, etc.
      if (['invite', 'inviteResponse', 'chat', 'game', 'score', 'end', 'history'].includes(data.type)) {
        const to = data.to;
        if (to && users[to]) {
          users[to].send(message);
        }
      }
    } catch (e) {}
  });

  ws.on('close', function() {
    if (username) {
      delete users[username];
      broadcastUserList();
    }
  });
});

console.log(`WebSocket server running on port ${PORT}`);
