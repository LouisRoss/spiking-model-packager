const { exec } = require("child_process");

var deleteModelDeployment = function(req, res) {
  const { modelName, deploymentName } = req.params;
  console.log(`Model packager received DELETE to delete deployment '${deploymentName}' from model '${modelName}'`);
  
  exec(`python model-deployment-deleter.py ${modelName} ${deploymentName}`, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      if (stderr) {
        console.log(`stderr: ${stderr}`);
      }
      res.status(503).send({ response: stderr });
    } else {
      console.log(`Deleted deployment '${deploymentName}' from model '${modelName}':\n${stdout}`);
      res.set('Access-Control-Allow-Origin', '*');
      var response = {
        response: `Deployment ${deploymentName} for model ${modelName} deleted`
      };
      res.json(response);
    }
  });
}

module.exports = deleteModelDeployment;
