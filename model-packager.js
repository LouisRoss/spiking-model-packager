const express = require('express');
const http = require('http');
const bodyParser = require('body-parser');
const path = require('path');
const net = require('net');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const { exec } = require("child_process");

let rawdata = fs.readFileSync('/configuration/configuration.json');
configuration = JSON.parse(rawdata);
console.log(configuration);

const inprogress = {};

const app = express();
const router = express.Router();

router.get('/package/progress/:packageId', (req, res) => {
  const { packageId } = req.params;
  console.log(`Modle packager received GET progress for packate ${packageId}`);
  
  const progress = inprogress[packageId];
  if (progress) {
    var response = {
      status: progress.status,
      completed: progress.completed,
      link: `${req.protocol}://${req.get('Host')}/package/progress/${packageId}`
    };
    res.json(response);
  
    if (progress.completed) {
      delete inprogress[packageId];
    }
  } else {
    res.status(503).send({ error: `Requested package ID ${packageId} does not exist`});
  }
});

router.post('/package', (req, res) => {
  let template = req.query.template;
  if (!template) {
    res.status(400).send({ error: 'Required template parameter not supplied'});
    return;
  } else {
    if (!template.endsWith('.json')) {
      template += '.json';
    }
  }
  const model = req.query.model;
  if (!model) {
    res.status(400).send({ error: 'Required model parameter not supplied'});
    return;
  }
  
  const packageId = uuidv4();
  const controller = new AbortController();
  const { signal } = controller;
  inprogress[packageId] = { controller, completed: false, status: "Packaging in progress" };
  exec(`python template-expander1.py ${template} ${model}`, { signal }, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      inprogress[packageId].status = "Packaging error " + error.message;
      if (stderr) {
        console.log(`stderr: ${stderr}`);
      }
    } else {
      inprogress[packageId].status = "Packaging complete with no error";
      console.log(`stdout: ${stdout}`);
    }
    inprogress[packageId].completed = true;
  });
  
  var response = {
    response: `Started packaging template ${template} to model ${model}`,
    link: `${req.protocol}://${req.get('Host')}/package/progress/${packageId}`
  };
  res.json(response);
});

var server = http.createServer(app);
const PORT = 5000;
app.use(bodyParser.json());
app.use('/', router);
app.use(express.static('public'));

server.listen(PORT, () => console.log(`Server running on port http://model-package:${PORT}`));
