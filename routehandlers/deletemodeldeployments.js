const { exec } = require("child_process");

var deleteModelDeployments = function(req, res) {
  const { modelName, deploymentName } = req.params;
  console.log(`Model packager received DELETE to delete deployments from model '${modelName}'`);
  
  exec(`python model-deployments-deleter.py ${modelName}`, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      if (stderr) {
        console.log(`stderr: ${stderr}`);
      }
      res.status(503).send({ response: stderr });
    } else {
      console.log(`Deleted deployments from model '${modelName}':\n${stdout}`);
      res.set('Access-Control-Allow-Origin', '*');
      var response = {
        response: `Deployments for model ${modelName} deleted`
      };
      res.json(response);
    }
  });
}

module.exports = deleteModelDeployments;
