const express = require('express');
const http = require('http');
const bodyParser = require('body-parser');
const cors = require("cors"); // enforce CORS, will be set to frontend URL when deployed

const fs = require('fs');

var singleton = require('./routehandlers/inprogress');
const inprogress = singleton.getInstance();
const getModels = require('./routehandlers/getmodels');
const getTemplates = require('./routehandlers/gettemplates');
const getModelTemplates = require('./routehandlers/getmodeltemplates');
const getModelPopulation = require('./routehandlers/getmodelpopulation');
const getModelExpansion = require('./routehandlers/getmodelexpansion');
const getModelProgress = require('./routehandlers/getmodelprogress');
const getPackageProgress = require('./routehandlers/getpackageprogress');
const putPackage = require('./routehandlers/putpackage');
const postModel = require('./routehandlers/postmodel');
const deleteModel = require('./routehandlers/deletemodel');
const getModelDeployments = require('./routehandlers/getmodeldeployments');
const getModelDeployment = require('./routehandlers/getmodeldeployment');
const putModelDeployment = require('./routehandlers/putmodeldeployment');
const deleteModelDeployment = require('./routehandlers/deletemodeldeployment');
const deleteModelDeployments = require('./routehandlers/deletemodeldeployments');


let rawdata = fs.readFileSync('/configuration/configuration.json');
configuration = JSON.parse(rawdata);
console.log(configuration);

const app = express();
app.use(cors());

const router = express.Router();

// Get the list of models that currently exist.
router.get('/models', [getModels]);

// Get the list of templates.
router.get('/templates', [getTemplates]);

// Get the list of templates for a specified model.
router.get('/model/:modelName/templates', [getModelTemplates]);

// Get the list of templates for a specified model.
router.get('/model/:modelName/population', [getModelPopulation]);

// Get the expansion of a specific template for a specified model.
router.get('/model/:modelName/expansion/:templateSequence', [getModelExpansion]);

// Check on model creation progress for previous POST model.
router.get('/model/progress/:modelId', [getModelProgress]);

// Check on packaging progress for previous PUT package.
router.get('/package/progress/:packageId', [getPackageProgress]);

// Accept the model name, and expand it.
router.put('/package/:modelName', [putPackage]);

// Accept the URL parameter modelName, and create the specified empty model.
router.post('/model/:modelName', [postModel]);

// Accept the URL parameter modelName, and delete the specified model.
router.delete('/model/:modelName', [deleteModel]);

// Get the list of deployments for a specified model.
router.get('/model/:modelName/deployments', [getModelDeployments]);

// Get the named deployment for a specified model.
router.get('/model/:modelName/deployment/:deploymentName', [getModelDeployment]);

// Accept the model name and deployment name, create a deployment within the model deployments.
router.put('/model/:modelName/deployment/:deploymentName', [putModelDeployment]);

// Accept the URL parameters modelName and deploymentName, and delete the specified deployment from the model.
router.delete('/model/:modelName/deployment/:deploymentName', [deleteModelDeployment]);

// Accept the URL parameter modelName, and delete the deployments from the model.
router.delete('/model/:modelName/deployments', [deleteModelDeployments]);

var server = http.createServer(app);
const PORT = 5000;
app.use(bodyParser.json());
app.use('/', router);
app.use(express.static('public'));

server.listen(PORT, () => console.log(`Server running on port http://model-packager:${PORT}`));
