var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var getPackageProgress = function(req, res) {
  const { packageId } = req.params;
  console.log(`Model packager received GET progress for package ${packageId}`);
  
  const progress = inprogress[packageId];
  if (progress) {
    var response = {
      status: progress.status,
      completed: progress.completed,
      link: `${req.protocol}://${req.get('Host')}/package/progress/${packageId}`
    };
    res.json(response);
  
    if (progress.completed) {
      delete inprogress[packageId];
    }
  } else {
    res.status(503).send({ error: `Requested package ID ${packageId} does not exist`});
  }
}

module.exports = getPackageProgress;
