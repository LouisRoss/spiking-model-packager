const h5model = require("./h5model.js");

var putModelInterconnects = function(req, res) {
  const { modelName } = req.params;

  const model = new h5model(modelName, () => {
    model.putInterconnectsToModel(req.body, response => {
      if (response.status == 201) {
        console.log(response.result);
        res.set('Access-Control-Allow-Origin', '*');
        res.json(response);
      }
      else {
        console.log(`Status: ${response.status}, error: ${response.result}`);
        res.status(response.status).send(response.result)
      }
    });
  });
}

module.exports = putModelInterconnects;
