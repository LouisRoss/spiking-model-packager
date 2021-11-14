const { v4: uuidv4 } = require('uuid');
const { exec } = require("child_process");

var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var putPackage = function(req, res) {
  const { modelName } = req.params;
  if (!modelName) {
    res.status(400).send({ error: 'Required modelName parameter not supplied'});
    return;
  }
  console.log(`PUT package for model ${modelName}, policies ${req.body}`);
  
  const packageId = uuidv4();
  const controller = new AbortController();
  const { signal } = controller;
  inprogress[packageId] = { controller, completed: false, progress: 0, status: "Packaging in progress", results: [] };
  exec(`python template-compiler.py ${modelName} ${req.body.join(" ")}`, { signal }, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      inprogress[packageId].status = `Model packaging error for model '${modelName}'` + error.message;
      if (stderr) {
        console.log(`stderr: ${stderr}`);
      }
    } else {
      inprogress[packageId].status = stdout;
      console.log(stdout);
    }
    inprogress[packageId].completed = true;
  });


  //const progressPerPolicy = Math.round(100 / req.body.length);
  //setTimeout(package, 100, packageId, modelName, progressPerPolicy, req.body);
  
  var response = {
    response: `Started packaging template to model ${modelName}`,
    link: `${req.protocol}://${req.get('Host')}/package/progress/${packageId}`
  };
  res.json(response);
}

var package = function (packageId, modelName, progressPerPolicy, policies) {
  if (policies.length == 0) {
    inprogress[packageId].status = "Packaging complete";
    inprogress[packageId].completed = true;
    inprogress[packageId].progress = 100;
    return;
  }

  policy = policies.splice(0, 1);   // Remove the first policy element.

  const { signal } = inprogress[packageId].controller;
  inprogress[packageId].status = `Packaging policy ${policy}`;

  exec(`python template-expander1.py ${modelName} ${policy}`, { signal }, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      inprogress[packageId].results.push(`Packaging error for ${policy}` + error.message);
      if (stderr) {
        console.error(`stderr: ${stderr}`);
      }
    } else {
      inprogress[packageId].results.push(`Packaging complete with no error for ${policy}`);
      console.log(`stdout: ${stdout}`);
    }

    inprogress[packageId].status = `Packaging complete for policy ${policy}`;
    inprogress[packageId].progress += progressPerPolicy;
    setTimeout(package, 100, packageId, modelName, progressPerPolicy, policies);
  });
}

module.exports = putPackage;
