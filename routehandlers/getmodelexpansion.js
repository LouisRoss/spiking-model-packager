const h5model = require("./h5model.js");

var getModelExpansion = function(req, res) {
  const { modelName, templateSequence } = req.params;

  const model = new h5model(modelName, () => {
    model.getExpansionFromModel(templateSequence, response => {
      if (model.responseStatus == 200) {
        console.log(model.responseSuccessPayload);
        res.set('Access-Control-Allow-Origin', '*');
        res.json(response);
      }
      else {
        console.log(`Status: ${model.responseStatus}, error: ${model.errorMessage}`);
        res.status(model.responseStatus).send(model.errorMessage)
      }
    });
  });
}

module.exports = getModelExpansion;
