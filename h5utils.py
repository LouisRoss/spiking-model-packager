import sys
import json
import requests
from h5Rest import h5Rest

class h5model:
  rootId = ""
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
    # Get the starting REST response, extract the group base element.
    groupBaseRest = self.restManager.getRest("")
    if groupBaseRest.status_code != 200:
      self.errorMessage = "Starting REST response contains no root link"
      responseStatus = 500
      return

    # Get the group base root links REST response, extract the list of domain links.
    # NOTE: domains in H5serv are individual files, which represent individual models.
    groupBase = groupBaseRest.json()
    rootId = groupBase["root"]
    rootLinkeRest = self.restManager.getRest("/groups/" + rootId + "/links")
    if rootLinkeRest.status_code != 200:
      self.errorMessage = "Root link REST response contains no sub-links"
      responseStatus = 500
      return

    rootLinkResponse = rootLinkeRest.json()
    domainLinks = rootLinkResponse["links"]

    #print([x["title"] for x in domainLinks])
    self.responseSuccessPayload = domainLinks
    self.responseStatus = 200

  def initializeModel(self):
    data = { 'link': { 'id': self.rootId, 'name': 'templates' }}
    response = self.restManager.postRest('/groups', json.dumps(data), True)
    print('Response from creating /templates group: ' + str(response.status_code) + ' = ' + response.reason)
    if response.ok:
      print(response.json())
      self.templatesGroupId = response.json()["id"]

    data = { 'link': { 'id': self.rootId, 'name': 'expansions' }}
    response = self.restManager.postRest('/groups', json.dumps(data), True)
    print('Response from creating /expansions group: ' + str(response.status_code) + ' = ' + response.reason)
    if response.ok:
      print(response.json())
      self.expansionsGroupId = response.json()["id"]
      data = { 'type': 'H5T_STD_I32LE', 'value': '0' }
      response = self.restManager.putRest('/groups/' + self.expansionsGroupId + '/attributes/maxindex', json.dumps(data), True)
      print('Response from creating /expansions group attribute maxindex: ' + str(response.status_code) + ' = ' + response.reason)

  def getExistingTemplates(self):
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
    #models = self.getExistingModels()
    #modelExists = next((x for x in models if x["title"].lower() == self.modelName.lower()), None)

    #if modelExists:
    #  return 0

    responseRest = self.restManager.putRest("", None, True)
    if responseRest.status_code == 201:
      response = responseRest.json()
      self.rootId = response["root"]
      self.initializeModel()
      return 0
    elif response.status_code == 409:
      print('Model ' + self.modelName + ' already exists, not creating')
      return 0
    else:
      self.failureReason = 'Model creating (PUT ' + self.modelName + ') failed with HTTP status ' + str(response.status_code)
      return 1

  def deleteModel(self):
    response = self.restManager.deleteRest("", True)

    print(response)
    return 0

  def addTemplateToModel(self, templateName, template):
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
    templateLink = next((x for x in templatesLinks if x["title"] == templateName), None)
    if templateLink:
      self.responseSuccessPayload = ["Template " + templateName + " already exists for model " + self.modelName]
      self.responseStatus = 200
      return

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

    dataSetResponse = dataSetRest.json()
    dataSetId = dataSetResponse["id"]

    payload = { "value": json.dumps(template) }
    dataValueRest = self.restManager.putRest('/datasets/' + dataSetId + '/value', json.dumps(payload), True)

  def addExpansionToModel(self, expansionName, expansion):
    if not self.expansionsGroupId:
      self.errorMessage = "Model file for '" + self.modelName + "' is malformed, has no 'expansions' group"
      self.responseStatus = 503
      return
    
    expansionsRest = self.restManager.getRest("/groups/" + self.expansionsGroupId + "/links", True)
    if expansionsRest.status_code != 200:
      self.errorMessage = "Model file for '" + self.modelName + "' 'expansions' group contains no sub-links"
      self.responseStatus = 503
      return

    dataSetId = ""
    expansionsLinks = expansionsRest.json()["links"]
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

    payload = { "value": expansion }
    dataValueRest = self.restManager.putRest('/datasets/' + dataSetId + '/value', json.dumps(payload), True)
