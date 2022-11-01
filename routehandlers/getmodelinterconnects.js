const h5model = require("./h5model.js");

var getModelInterconnects = function(req, res) {
  const { modelName } = req.params;

  const model = new h5model(modelName, () => {
    model.getInterconnectsFromModel(response => {
      if (response.status == 200) {
        res.set('Access-Control-Allow-Origin', '*');
        res.json(response.result);
      }
      else {
        console.log(response);
        res.status(response.status).send(response.result)
      }
    });
  });
}

module.exports = getModelInterconnects;
