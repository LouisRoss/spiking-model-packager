const { v4: uuidv4 } = require('uuid');
const { exec } = require("child_process");

var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var putPackage = function(req, res) {
  let template = req.query.template;
  if (!template) {
    res.status(400).send({ error: 'Required template parameter not supplied'});
    return;
  } else {
    if (!template.endsWith('.json')) {
      template += '.json';
    }
  }
  const model = req.query.model;
  if (!model) {
    res.status(400).send({ error: 'Required model parameter not supplied'});
    return;
  }
  
  const packageId = uuidv4();
  const controller = new AbortController();
  const { signal } = controller;
  inprogress[packageId] = { controller, completed: false, status: "Packaging in progress" };
  exec(`python template-expander1.py ${template} ${model}`, { signal }, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      inprogress[packageId].status = "Packaging error " + error.message;
      if (stderr) {
        console.log(`stderr: ${stderr}`);
      }
    } else {
      inprogress[packageId].status = "Packaging complete with no error";
      console.log(`stdout: ${stdout}`);
    }
    inprogress[packageId].completed = true;
  });
  
  var response = {
    response: `Started packaging template ${template} to model ${model}`,
    link: `${req.protocol}://${req.get('Host')}/package/progress/${packageId}`
  };
  res.json(response);
}

module.exports = putPackage;
