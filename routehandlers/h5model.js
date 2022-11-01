const axios = require('axios');
const fs = require('fs');

class h5model {
  constructor(modelName, initHandler) {
    this.modelName = modelName
    this.failureReason = ""

    let rawdata = fs.readFileSync('/configuration/configuration.json');
    this.configuration = JSON.parse(rawdata);

    this.persistHost = this.configuration['services']['modelPersist']['host'];
    this.persistPort = this.configuration['services']['modelPersist']['port'];
    this.persistBaseDomain = this.configuration['services']['modelPersist']['basedomain'];

    this.modelBaseUrl = this.persistHost + ":" + this.persistPort;
    this.fileDomain = this.modelName + '.' + this.persistBaseDomain;
    
    this.responseStatus = 200;
    this.responseSuccessPayload = '';
    this.errorMessage = '';
    this.restManager = undefined;

    // When enumerating models, we can be created with an empty model name.  This is ok.
    if (modelName && modelName.length > 0) {
      axios.get(this.modelBaseUrl + '?host=' + this.fileDomain)
      .then(rootResponse => {
        this.rootId = rootResponse.data.root;

        axios.get(this.modelBaseUrl + '/groups/' + this.rootId + '/links' + '?host=' + this.fileDomain)
        .then(rootGroupResponse => {
          const rootTemplatesLink = rootGroupResponse.data.links.find(x => x.title === 'templates');
          this.templatesGroupId = rootTemplatesLink ? rootTemplatesLink.id : undefined;
          const rootExpansionsLink = rootGroupResponse.data.links.find(x => x.title === 'expansions');
          this.expansionsGroupId = rootExpansionsLink ? rootExpansionsLink.id : undefined;
          const rootPopulationLink = rootGroupResponse.data.links.find(x => x.title === 'population');
          this.populationDatasetId = rootPopulationLink ? rootPopulationLink.id : undefined;
          const rootConnectionLink = rootGroupResponse.data.links.find(x => x.title === 'connections');
          this.connectionsDatasetId = rootConnectionLink ? rootConnectionLink.id : undefined;

          initHandler();
        });
      })
      .catch(error => {
        console.log(error);
        this.errorMessage = error;
        this.responseStatus = 503
        initHandler();
      });
    }
    else {
      initHandler();
    }
  }

  //
  // Get the population dataset for this model.  Return through the callback.
  //
  getPopulation(populationHandler) {
    if (!this.populationDatasetId) {
      this.errorMessage = `Model file for '${this.modelName}' is malformed, has no 'population' dataset`;
      this.responseStatus = 503;
      return false;
    }

    axios.get(this.modelBaseUrl + '/datasets/' + this.populationDatasetId + '/value' + '?host=' + this.fileDomain)
    .then(populationDatasetResponse => {
      this.responseStatus = 200;
      populationHandler({ 'status': 200, 'result': JSON.parse(populationDatasetResponse.data.value[0]) });
    })
    .catch(error => {
      console.log(error);
      this.errorMessage = error;
      populationHandler({ 'status': 400, 'result': error} );
    });
  }

  //
  // Get the specified expansion from the model.  Return through the callback.
  //
  getExpansionFromModel(sequence, expansionHandler) {
    console.log(`Get expansion ${sequence} from model ${this.modelName}`);

    // Get the /expansions group description from the h5serv, and extract the 'links' element.
    if (!this.expansionsGroupId) {
      this.errorMessage = `Model file for '${this.modelName}' is malformed, has no 'expansions' group`
      this.responseStatus = 503
      expansionHandler([]);
    }
    
    // We will need metadata from the population so get that first.
    this.getPopulation(populationResult => {
      if (populationResult.status !== 200) {
        expansionHandler([]);
        return;
      }

      const templateData = populationResult.result.templates[sequence]
      console.log(`Got template data for sequence ${sequence}, getting expansion group`);

      axios.get(this.modelBaseUrl + '/groups/' + this.expansionsGroupId + '/links' + '?host=' + this.fileDomain)
      .then(expansionsGroupResponse => {
        const expansionsLinks = expansionsGroupResponse.data.links;

        // If the 'expansions' group has an existing dataset link for the specified expansion sequence, use its Id, otherwise make it and use the new Id.
        const expansionLink = expansionsLinks.find(x => x.title === sequence);
        if (expansionLink === undefined) {
          this.errorMessage = `Model file for '${this.modelName}' 'expansions' group does not contain sequence ${sequence}`;
          this.responseStatus = 503
          expansionHandler([]);
          return;
        }
    
        const dataSetId = expansionLink["id"]
        console.log(`Got expansion dataset Id ${dataSetId} for expansion ${sequence}, getting dataset`);
        axios.get(this.modelBaseUrl + '/datasets/' + dataSetId + '/value' + '?host=' + this.fileDomain)
        .then(expansionsGroupResponse => {
          // Formulate the lowest index (starting index for the template) and sum of all counts (total count for the template).
          var startingIndex = 1000000;
          var totalCount = 0;
          for (var indexName in templateData.indexes) {
            const propertyIndex = templateData.indexes[indexName]['index'];
            startingIndex = startingIndex < propertyIndex ? startingIndex : propertyIndex;
            totalCount += templateData.indexes[indexName]['count'];
          }

          var expansionValue = {};
          expansionValue['startingindex'] = startingIndex;
          expansionValue['totalcount'] = totalCount;
          expansionValue['value'] = expansionsGroupResponse.data.value;
          console.log(`Found expansion for sequence ${sequence} from model '${this.modelName}' with ${expansionValue['value'].length} values`);

          this.responseSuccessPayload = `Successfully returned expansion for sequence ${sequence} from model '${this.modelName}' with ${expansionValue['value'].length} values`;
          this.responseStatus = 200
          expansionHandler(expansionValue);
          return;
        })
        .catch(error => {
          console.log(error);
          this.errorMessage = error;
          this.responseStatus = 503
          expansionHandler([]);
          return;
        });
      })
      .catch(error => {
        console.log(error);
        this.errorMessage = error;
        this.responseStatus = 503
        expansionHandler([]);
        return;
      });
    });
  }

  //
  // Get the interconnects from the model.  Return through the callback.
  //
  getInterconnectsFromModel(interconnectHandler) {
    console.log(`Get interconnects from model ${this.modelName}`);

    if (!this.connectionsDatasetId) {
      this.errorMessage = `Model file for '${this.modelName}' is malformed, has no 'connections' dataset`;
      interconnectHandler({ 'status': 503, 'result': this.errorMessage} );
      return;
    }

    axios.get(this.modelBaseUrl + '/datasets/' + this.connectionsDatasetId + '/value' + '?host=' + this.fileDomain)
    .then(connectionsDatasetResponse => {
      var response = JSON.parse(connectionsDatasetResponse.data.value[0]);
      console.log(response);
      interconnectHandler({ 'status': 200, 'result': response });
    })
    .catch(error => {
      console.log(error);
      interconnectHandler({ 'status': 400, 'result': error} );
    });
  }

  //
  // Put the interconnects to the model.  Return through the callback.
  //
  putInterconnectsToModel(interconnects, interconnectHandler) {
    console.log(`Put interconnects to model ${this.modelName}`);
    console.log(interconnects);

    if (!this.connectionsDatasetId) {
      this.errorMessage = `Model file for '${this.modelName}' is malformed, has no 'connections' dataset`;
      interconnectHandler({ 'status': 503, 'result': this.errorMessage} );
      return;
    }

    const payload = { 'value': JSON.stringify(interconnects) };
    const headers = { 'Accept': 'application/json' };

    axios.put(this.modelBaseUrl + '/datasets/' + this.connectionsDatasetId + '/value' + '?host=' + this.fileDomain, payload, headers)
    .then(connectionsDatasetResponse => {
      interconnectHandler({ 'status': 201, 'result': "Successfully added interconnects to model '" + this.modelName + "'" });
    })
    .catch(error => {
      console.log(error);
      interconnectHandler({ 'status': 503, 'result': error} );
    });
  }
}

module.exports = h5model;
