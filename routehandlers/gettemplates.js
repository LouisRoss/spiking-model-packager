const fs = require('fs');

var getTemplates = function(req, res) {
  fs.readdir('/templates', (err, files) => {
    if (err) {
      console.log(`error: ${err.message}`);
      res.set('Access-Control-Allow-Origin', '*');
      res.status(503).send(err.message);
    } else {
      console.log([...files])
      res.set('Access-Control-Allow-Origin', '*');
      res.json([...files.map(file => file.substring(0, file.length - 5))] );
    }
  });
}

module.exports = getTemplates;
