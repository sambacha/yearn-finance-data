const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8080');

ws.on('open', function open() {
  ws.send('something');
});

ws.on('message', function incoming(data) {
//  console.log(data);
});


//const nws = new WebSocket('wss://stream.binance.com:9443/ws/ethbtc@ticker');
const nws = new WebSocket('wss://stream.binance.com:9443/ws/!ticker@arr');

nws.on('open', function open() {

console.log('open')

});

nws.on('message', function incoming(data) {
//  console.log(data);
ws.send(data);
});
