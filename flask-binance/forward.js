var WebSocketServer = require("ws").Server;

var wss = new WebSocketServer({ port: 8080 });

wss.on("connection", function connection(ws) {
  ws.on("message", function (message) {
    //  console.log(message);
    wss.broadcast(message);
  });
});

wss.broadcast = function broadcast(msg) {
  //   console.log(msg);
  wss.clients.forEach(function each(client) {
    client.send(msg);
  });
};
