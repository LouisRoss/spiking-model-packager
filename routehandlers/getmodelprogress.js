var singleton = require('./inprogress');
const inprogress = singleton.getInstance();

var getModelProgress = function(req, res) {
  const { modelId } = req.params;
  console.log(`Model packager received GET progress for model ${modelId}`);
  
  const progress = inprogress[modelId];
  if (progress) {
    var response = {
      status: progress.status,
      completed: progress.completed,
      link: `${req.protocol}://${req.get('Host')}/model/progress/${modelId}`
    };
    res.set('Access-Control-Allow-Origin', '*');
    res.json(response);
  
    if (progress.completed) {
      delete inprogress[modelId];
    }
  } else {
    res.set('Access-Control-Allow-Origin', '*');
    res.status(503).send({ error: `Requested model ID ${modelId} does not exist`});
  }
}

module.exports = getModelProgress;
