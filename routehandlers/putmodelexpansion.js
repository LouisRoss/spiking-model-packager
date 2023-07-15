const { v4: uuidv4 } = require('uuid');
const { exec } = require("child_process");

var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var putModelExpansion = function(req, res) {
  const { modelName, templateSequence } = req.params;
  if (!modelName) {
    res.status(400).send({ error: 'Required modelName parameter not supplied'});
    return;
  }
  if (!templateSequence) {
    res.status(400).send({ error: 'Required template sequence parameter not supplied'});
    return;
  }
  console.log(`PUT expansion for model ${modelName}, sequence ${templateSequence}`);

  var expansion = JSON.stringify(req.body);
  if (!expansion) {
    expansion = '[]'
  }
  console.log(`Expansion: '${expansion}'`);

  const expansionId = uuidv4();
  const controller = new AbortController();
  const { signal } = controller;
  inprogress[expansionId] = { controller, completed: false, progress: 0, status: "Expansion write in progress", results: [] };
  exec(`python model-expansion-putter.py ${modelName} ${templateSequence} ${expansion}`, { signal }, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      inprogress[expansionId].status = `Model expansion write error for model '${modelName}', sequence ${templateSequence}` + error.message;
      if (stderr) {
        console.log(`stderr: ${stderr}`);
      }
    } else {
      inprogress[expansionId].status = stdout;
      console.log(stdout);
    }
    inprogress[expansionId].completed = true;
  });


  //const progressPerPolicy = Math.round(100 / req.body.length);
  //setTimeout(package, 100, expansionId, modelName, progressPerPolicy, req.body);
  
  var response = {
    response: `Started writing expansion to model ${modelName}, sequence ${templateSequence}`,
    link: `${req.protocol}://${req.get('Host')}/expansion/progress/${expansionId}`
  };
  res.json(response);
}

module.exports = putModelExpansion;
