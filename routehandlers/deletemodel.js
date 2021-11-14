const { v4: uuidv4 } = require('uuid');
const { exec } = require("child_process");

var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var deleteModel = function(req, res) {
  const { modelName } = req.params;
  console.log(`Model packager received DELETE to delete model '${modelName}'`);
  
  const modelId = uuidv4();
  const controller = new AbortController();
  const { signal } = controller;
  inprogress[modelId] = { controller, completed: false, status: `Deletion of model '${modelName}' in progress` };
  exec(`python model-deleter.py ${modelName}`, { signal }, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      inprogress[modelId].status = `Model deletion error for model '${modelName}'` + error.message;
      if (stderr) {
        console.log(`stderr: ${stderr}`);
      }
    } else {
      inprogress[modelId].status = `Model deletion for '${modelName}' complete with no error: ${stdout}`;
      console.log(`stdout: ${stdout}`);
    }
    inprogress[modelId].completed = true;
  });
  
  var response = {
    status: `Started deleting model '${modelName}'`,
    completed: false,
    link: `${req.protocol}://${req.get('Host')}/model/progress/${modelId}`
  };
  res.set('Access-Control-Allow-Origin', '*');
  res.json(response);
}

module.exports = deleteModel;
