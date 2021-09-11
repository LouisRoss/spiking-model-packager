import sys
import json
import requests
from h5Rest import h5Rest

class h5model:
  rootId = None
  groups = {}
  datasets = {}
  modelName = ""
  templatesGroupId = None
  expansionsGroupId = None
  configuration = None
  responseStatus = 200
  responseSuccessPayload = ""
  errorMessage = ""
  restManager = None

  def __init__(self, modelName):
    self.restManager = h5Rest(modelName)
    self.modelName = modelName
    self.failureReason = ""

    f = open('/configuration/configuration.json')
    self.configuration = json.load(f)

    # When enumerating models, we can be created with an empty model name.  This is ok.
    if (len(modelName) > 0):
      modelRest = self.restManager.getRest("", True)
      if modelRest.status_code == 200:
        self.rootId = modelRest.json()['root']

        rootGroupRest = self.restManager.getRest("/groups/" + self.rootId + "/links", True)
        if rootGroupRest.status_code == 200:
          rootGroup = rootGroupRest.json()
          rootTemplatesLink = next((x for x in rootGroup["links"] if x["title"] == "templates"), None)
          self.templatesGroupId = rootTemplatesLink["id"] if rootTemplatesLink else None
          rootExpansionsLink = next((x for x in rootGroup["links"] if x["title"] == "expansions"), None)
          self.expansionsGroupId = rootExpansionsLink["id"] if rootExpansionsLink else None


  def getExistingModels(self):
    """ Enumerate all existing model files.
    """
    # Get the starting REST response, extract the group base element.
    groupBaseRest = self.restManager.getRest("")
    if groupBaseRest.status_code != 200:
      self.errorMessage = "Starting REST response contains no root link"
      responseStatus = 500
      return

    # Get the group base root links REST response, extract the list of domain links.
    # NOTE: domains in H5serv are individual files, which represent individual models.
    rootId = groupBaseRest.json()["root"]
    rootLinkRest = self.restManager.getRest("/groups/" + rootId + "/links")
    if rootLinkRest.status_code != 200:
      self.errorMessage = "Root link REST response contains no sub-links"
      responseStatus = 500
      return

    domainLinks = rootLinkRest.json()["links"]

    #print([x["title"] for x in domainLinks])
    self.responseSuccessPayload = domainLinks
    self.responseStatus = 200

  def initializeModel(self):
    """ Immediately after a new model file is created, it must be initialized here.
    """

    # Create the templates group as a subgroup of the root.
    data = { 'link': { 'id': self.rootId, 'name': 'templates' }}
    responseRest = self.restManager.postRest('/groups', json.dumps(data), True)
    if not responseRest.ok:
      self.failureReason = "Unable to create 'templates' group for model '" + self.modelName + "': " + responseRest.reason
      self.responseStatus = 500
      return

    self.templatesGroupId = responseRest.json()["id"]

    # Create the expansions group as a subgroup of the root.
    data = { 'link': { 'id': self.rootId, 'name': 'expansions' }}
    responseRest = self.restManager.postRest('/groups', json.dumps(data), True)
    if not responseRest.ok:
      self.failureReason = "Unable to create 'expansions' group for model '" + self.modelName + "': " + responseRest.reason
      self.responseStatus = 500
      return

    self.expansionsGroupId = responseRest.json()["id"]

    # Create the maxindex attribute in the expansions group.
    data = { 'type': 'H5T_STD_I32LE', 'value': '0' }
    responseRest = self.restManager.putRest('/groups/' + self.expansionsGroupId + '/attributes/maxindex', json.dumps(data), True)
    if not responseRest.ok:
      self.failureReason = "Unable to create 'maxindex' attribute in the 'expansions' group for model '" + self.modelName + "': " + responseRest.reason
      self.responseStatus = 500
      return

    self.responseSuccessPayload = "Successfully created model '" + self.modelName + "'"
    self.responseStatus = 200

  def getExistingTemplates(self):
    """ Get a list containing the existing templates for this model.
    """
    if not self.templatesGroupId:
      self.errorMessage = "Model file for '" + self.modelName + "' is malformed, has no 'templates' group"
      self.responseStatus = 503
      return
    
    templatesRest = self.restManager.getRest("/groups/" + self.templatesGroupId + "/links", True)
    if templatesRest.status_code != 200:
      self.errorMessage = "Model file for '" + self.modelName + "' 'templates' group contains no sub-links"
      self.responseStatus = 503
      return

    templatesLinks = templatesRest.json()["links"]
    self.responseSuccessPayload = [link["title"] for link in templatesLinks]
    self.responseStatus = 200


  def createModel(self):
    """ Create a model file for this model object.
    """

    responseRest = self.restManager.putRest("", None, True)
    if responseRest.status_code == 201:
      response = responseRest.json()
      self.rootId = response["root"]
      self.initializeModel()
      # NOTE: Leave successful payload the status to initializeModel()
      return
    elif responseRest.status_code == 409:
      self.responseSuccessPayload = 'Model ' + self.modelName + ' already exists, not creating'
      self.responseStatus = 200
      return
    else:
      self.failureReason = 'Model creating (PUT ' + self.modelName + ') failed with HTTP status ' + str(response.status_code)
      self.responseStatus = 503
      return

  def deleteModel(self):
    """ Delete the whole model file from persistent store.
    """
    deleteRest = self.restManager.deleteRest("", True)
    if deleteRest.status_code != 200:
      self.errorMessage = "Unable to delete Model '" + self.modelName + "': " + deleteRest.reason
      self.responseStatus = 503
      return

    #print(deleteRest)
    self.responseSuccessPayload = "Successfully deleted model '" + self.modelName + "'"
    self.responseStatus = 200

  def addTemplateToModel(self, templateName, template):
    """ Record the named template into persistent store.
        templateName    The name of the template.
        template        The template object.  This will be rendered as json and stored as a string.
    """

    # Get the /templates group description from the h5serv, and extract the 'links' element.
    if not self.templatesGroupId:
      self.errorMessage = "Model file for '" + self.modelName + "' is malformed, has no 'templates' group"
      self.responseStatus = 503
      return
    
    templatesRest = self.restManager.getRest("/groups/" + self.templatesGroupId + "/links", True)
    if templatesRest.status_code != 200:
      self.errorMessage = "Model file for '" + self.modelName + "' 'templates' group contains no sub-links"
      self.responseStatus = 503
      return

    templatesLinks = templatesRest.json()["links"]

    # If a dataset for the template already exists, we are done.
    templateLink = next((x for x in templatesLinks if x["title"] == templateName), None)
    if templateLink:
      self.responseSuccessPayload = ["Template " + templateName + " already exists for model " + self.modelName]
      self.responseStatus = 200
      return

    # First create the dataset with the required shape.
    templateData = {
      "type": {
          "class": "H5T_STRING",
          "length": "H5T_VARIABLE",
          "charSet": "H5T_CSET_ASCII",
          "strpad": "H5T_STR_NULLTERM"
      },
      "shape": [1],
      "link": {
          "id": self.templatesGroupId,
          "name": templateName
      }
    }

    dataSetRest = self.restManager.postRest('/datasets', json.dumps(templateData), True)
    if dataSetRest.status_code != 201:
      self.errorMessage = "Unable to add template " + templageName + " to Model file for '" + self.modelName
      self.responseStatus = 503
      return

    # After creating the dataset, write the value into the dataset, a JSON-formatted string representing the template.
    dataSetResponse = dataSetRest.json()
    dataSetId = dataSetResponse["id"]

    payload = { "value": json.dumps(template) }
    dataValueRest = self.restManager.putRest('/datasets/' + dataSetId + '/value', json.dumps(payload), True)
    if dataValueRest.status_code != 200:
      self.errorMessage = "Unable to add template " + templateName + " data to Model file for '" + self.modelName + "'"
      self.responseStatus = 503
      return

    self.responseSuccessPayload = "Successfully added template '" + templateName + "' to model '" + self.modelName + "'"
    self.responseStatus = 201


  def addExpansionToModel(self, expansionName, nextIndex, expansion):
    """ Record the specified expansion of the named template into persistent store.
        expansionName   The name of the template that this is an expansion of.
        nextIndex       The next number of neurons needed for this expansion.
        expansion       A list of connections.  Each connection is a list in the form of
                        [from, to, strength].
    """

    # Get the /expansions group description from the h5serv, and extract the 'links' element.
    if not self.expansionsGroupId:
      self.errorMessage = "Model file for '" + self.modelName + "' is malformed, has no 'expansions' group"
      self.responseStatus = 503
      return
    
    expansionsRest = self.restManager.getRest("/groups/" + self.expansionsGroupId + "/links", True)
    if expansionsRest.status_code != 200:
      self.errorMessage = "Model file for '" + self.modelName + "' 'expansions' group contains no sub-links"
      self.responseStatus = 503
      return

    expansionsLinks = expansionsRest.json()["links"]

    # If the 'expansions' group has an existing dataset link for the specified expansion, use its Id, otherwise make it and use the new Id.
    dataSetId = ""
    dataSetCreated = False
    expansionLink = next((x for x in expansionsLinks if x["title"] == expansionName), None)
    if expansionLink:
      dataSetId = expansionLink["id"]
    else:
      expansionData = {
        "type": "H5T_IEEE_F32LE",
        "shape": [len(expansion), 3],
        "link": {
            "id": self.expansionsGroupId,
            "name": expansionName
        }
      }

      dataSetRest = self.restManager.postRest('/datasets', json.dumps(expansionData), True)
      if dataSetRest.status_code != 201:
        self.errorMessage = "Unable to add expansion " + expansionName + " to Model file for '" + self.modelName
        self.responseStatus = 503
        return

      dataSetResponse = dataSetRest.json()
      dataSetId = dataSetResponse["id"]
      dataSetCreated = True

    # Add the expansion as the dataset value, either overwriting the old dataset or filling in the new one.
    payload = { "value": expansion }
    dataValueRest = self.restManager.putRest('/datasets/' + dataSetId + '/value', json.dumps(payload), True)
    if dataValueRest.status_code != 200:
      self.errorMessage = "Unable to add expansion " + expansionName + " data to Model file for '" + self.modelName + "'"
      self.responseStatus = 503
      return

    # Update the 'maxindex' attribute by summing in the count of neurons just added in this expansion.
    if dataSetCreated:
      print("Getting current value of maxindex attribute")
      maxIndexRest = self.restManager.getRest('/groups/' + self.expansionsGroupId + '/attributes/maxindex', True)
      if maxIndexRest.status_code != 200:
        print('Returned status is ' + str(maxIndexRest.status_code))
        self.errorMessage = "Unable to update maxindex attribute to Model file for '" + self.modelName + "'"
        self.responseStatus = 503
        return

      # Read the current value of maxindex, add in the number of neurons for this expansion.
      # NOTE: Although the docs say writing will overwrite an existing attribute, it needs to be deleted first.
      maxIndexAttr = maxIndexRest.json()
      maxindex = maxIndexAttr["value"]
      data = { 'type': 'H5T_STD_I32LE', 'value': maxindex + nextIndex }
      self.restManager.deleteRest('/groups/' + self.expansionsGroupId + '/attributes/maxindex', True)
      response = self.restManager.putRest('/groups/' + self.expansionsGroupId + '/attributes/maxindex', json.dumps(data), True)
      if response.status_code != 201:
        self.errorMessage = "Unable to update maxindex attribute of expansion " + expansionName + " in Model file '" + self.modelName + "'"
        self.responseStatus = 503
        return

    self.responseSuccessPayload = "Successfully added expansion '" + expansionName + "' to model '" + self.modelName + "'"
    self.responseStatus = 201
