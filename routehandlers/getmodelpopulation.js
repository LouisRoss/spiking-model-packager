const { exec } = require("child_process");

var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var getModelPopulation = function(req, res) {
  const { modelId } = req.params;
  exec(`python model-population-getter.py ${modelId}`, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      if (stdout) {
        console.log(`stdout: ${stdout}`);
      }
      errorResponse = JSON.parse(stdout);
      res.status(errorResponse.status).send(errorResponse.message)
    } else {
      console.log(`stdout: ${stdout}`);
      res.set('Access-Control-Allow-Origin', '*');
      res.json(JSON.parse(stdout));
    }
  });
}

module.exports = getModelPopulation;
