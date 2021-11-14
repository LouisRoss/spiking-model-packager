const { exec } = require("child_process");

var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var getModelDeloyment = function(req, res) {
  const { modelName, deploymentName } = req.params;
  exec(`python model-deployment-getter.py ${modelName} ${deploymentName}`, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      if (stdout) {
        console.log(`stdout: ${stdout}`);
      }
      errorResponse = JSON.parse(stdout);
      res.status(errorResponse.status).send(errorResponse.message)
    } else {
      console.log(`Deployment ${deploymentName} for model ${modelName}: ${stdout}`);
      res.set('Access-Control-Allow-Origin', '*');
      res.json(JSON.parse(stdout));
    }
  });
}

module.exports = getModelDeloyment;
