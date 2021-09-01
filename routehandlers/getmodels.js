const { exec } = require("child_process");

var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var getModels = function(req, res) {
  exec(`python model-enumerator.py`, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      if (stderr) {
        console.log(`stderr: ${stderr}`);
      }
      res.status(error.code).send(error.message)
    } else {
      console.log(`stdout: ${stdout}`);
      res.set('Access-Control-Allow-Origin', '*');
      res.json(JSON.parse(stdout));
    }
  });
}

module.exports = getModels;
