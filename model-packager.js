const express = require('express');
const http = require('http');
const bodyParser = require('body-parser');
const path = require('path');
const net = require('net');
const fs = require('fs');

let rawdata = fs.readFileSync('/configuration/configuration.json');
let configuration = JSON.parse(rawdata);
console.log(configuration);


const app = express();
const router = express.Router();

router.get('/:command', (req, res) => {
  const { command } = req.params;
  console.log(`backend received GET from resoure ${command}`);

  if (command == 'status') {
  } else {
    var response = { response: `Unrecognized GET command resource ${command}` };
    res.json(response);
  }
});

router.post('/:command', (req, res) => {
  const { command } = req.params;

  var response = { response: `Unrecognized POST command resource ${command}` };
  if (command == 'connection') {
  }

  res.json(response);
});

var server = http.createServer(app);
const PORT = 5000;
app.use(bodyParser.json());
app.use('/', router);
app.use(express.static('public'));

server.listen(PORT, () => console.log(`Server running on port http://model-package:${PORT}`));
