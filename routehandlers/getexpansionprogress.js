var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var getExpansionProgress = function(req, res) {
  const { expansionId } = req.params;
  console.log(`Model packager received GET progress for expansion ${expansionId}`);
  
  const progress = inprogress[expansionId];
  if (progress) {
    var response = {
      status: progress.status,
      completed: progress.completed,
      link: `${req.protocol}://${req.get('Host')}/expansion/progress/${expansionId}`
    };
    res.set('Access-Control-Allow-Origin', '*');
    res.json(response);
  
    if (progress.completed) {
      delete inprogress[expansionId];
    }
  } else {
    res.set('Access-Control-Allow-Origin', '*');
    res.status(503).send({ error: `Requested model ID ${expansionId} does not exist`});
  }
}

module.exports = getExpansionProgress;
