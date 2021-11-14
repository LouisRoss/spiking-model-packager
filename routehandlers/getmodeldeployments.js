const { exec } = require("child_process");

var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var getModelDeployments = function(req, res) {
  const { modelName } = req.params;
  exec(`python model-deployments-getter.py ${modelName}`, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      if (stdout) {
        console.log(`stdout: ${stdout}`);
      }
      errorResponse = JSON.parse(stdout);
      res.status(errorResponse.status).send(errorResponse.message)
    } else {
      console.log(`Model ${modelName} deployments: ${stdout}`);
      res.set('Access-Control-Allow-Origin', '*');
      res.json(JSON.parse(stdout));
    }
  });
}

module.exports = getModelDeployments;
