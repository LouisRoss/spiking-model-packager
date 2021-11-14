const { exec } = require("child_process");

var putModelDeloyment = function(req, res) {
  const { modelName, deploymentName } = req.params;
  console.log(req.body);
  console.log(`PUT deployment ${deploymentName} for model ${modelName}, servers ${req.body}`);

  exec(`python model-deployment-putter.py ${modelName} ${deploymentName} ${req.body.join(" ")}`, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      if (stdout) {
        console.log(`stdout: ${stdout}`);
      }
      errorResponse = JSON.parse(stdout);
      res.status(errorResponse.status).send(errorResponse.message)
    } else {
      console.log(`Deployment ${deploymentName} for model ${modelName} created:\n${stdout}`);
      res.set('Access-Control-Allow-Origin', '*');
      var response = {
        response: `Deployment ${deploymentName} for model ${modelName} created`
      };
      res.json(response);
    }
  });
}

module.exports = putModelDeloyment;
