const { exec } = require("child_process");

var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var getModelExpansion = function(req, res) {
  const { modelName, templateSequence } = req.params;
  exec(`python model-expansion-getter.py ${modelName} ${templateSequence}`, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      if (stdout) {
        console.log(`stdout: ${stdout}`);
      }
      errorResponse = JSON.parse(stdout);
      res.status(errorResponse.status).send(errorResponse.message)
    } else {
      //console.log(`stdout: ${stdout}`);
      console.log(`Successfully retrieved expansion ${templateSequence} from model '${modelName}'`)
      res.set('Access-Control-Allow-Origin', '*');
      res.json(JSON.parse(stdout));
    }
  });
}

module.exports = getModelExpansion;
