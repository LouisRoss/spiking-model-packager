import sys
import json
import requests
from proxyurl import ProxyUrl


class h5model:
  rootId = ""
  groups = {}
  datasets = {}
  modelName = ""
  templatesGroupId = ""
  expansionsGroupId = ""
  persistHost = ""
  persistPort = ""
  persistBaseDomain = ""
  headers = { 'Accept': 'application/json' }
  configuration = None
  urlConverter = None
  responseStatus = 200
  responseSuccessPayload = ""
  errorMessage = ""

  def __init__(self, modelName):
    self.modelName = modelName
    self.failureReason = ""

    f = open('/configuration/configuration.json')
    self.configuration = json.load(f)

    self.persistHost = self.configuration["services"]["modelPersist"]["host"]
    self.persistPort = self.configuration["services"]["modelPersist"]["port"]
    self.persistBaseDomain = self.configuration["services"]["modelPersist"]["basedomain"]
    self.urlConverter = ProxyUrl(self.persistHost, self.persistPort)

  def getRest(self, url, addHost=False):
    proxyUrl = self.urlConverter.ComposeProxy(url + '?host=' + self.modelDomain() if addHost else url)
    #print('GETting from URL: ' + proxyUrl)

    response = requests.get(proxyUrl, headers=self.headers).json()
    #print(response)
    #print()
    return response

  def putRest(self, url, data, addHost=False):
    proxyUrl = self.urlConverter.ComposeProxy(url + '?host=' + self.modelDomain() if addHost else url)
    print('PUTting to URL: ' + proxyUrl)

    response = requests.put(proxyUrl, headers=self.headers, data=data)
    #print(response)
    #print()
    return response

  def postRest(self, url, data, addHost=False):
    headers = self.headers
    headers['host'] = self.modelDomain()
    proxyUrl = self.urlConverter.ComposeProxy(url)
    print('POSTting to URL: ' + proxyUrl)

    response = requests.post(proxyUrl, headers=headers, data=data)
    #print(response)
    #print()
    return response

  def deleteRest(self, url, addHost=False):
    proxyUrl = self.urlConverter.ComposeProxy(url + '?host=' + self.modelDomain() if addHost else url)
    print('DELETEing URL: ' + proxyUrl)

    response = requests.delete(proxyUrl, headers=self.headers)
    #print(response)
    #print()
    return response

  def getRestStep(self, url, key, addHost=False):
    response = self.getRest(url, addHost)
    hrefElement = next((x for x in response["hrefs"] if x["rel"] == key), None)
    return hrefElement

  def modelBaseUrl(self):
    return self.persistHost + ":" + self.persistPort

  def modelDomain(self):
    return self.modelName + '.' + self.persistBaseDomain

  def getExistingModels(self):
    # Get the starting REST response, extract the group base element.
    groupBase = self.getRest(self.modelBaseUrl())
    if groupBase == None:
      self.errorMessage = "Starting REST response contains no href for 'groupbase'"
      responseStatus = 500

    # Get the group base root links REST response, extract the list of domain links.
    # NOTE: domains in H5serv are individual files, which represent individual models.
    rootId = groupBase["root"]
    rootLinkResponse = self.getRest(self.modelBaseUrl() + "/groups/" + rootId + "/links")
    domainLinks = rootLinkResponse["links"]

    #print([x["title"] for x in domainLinks])
    self.responseSuccessPayload = domainLinks
    self.responseStatus = 200

  def initializeModel(self):
    modelRest = self.getRest(self.modelBaseUrl(), True)
    self.rootId = modelRest['root']
    print("Model '" + self.modelName + "' root Id = " + str(self.rootId))

    data = { 'link': { 'id': self.rootId, 'name': 'templates' }}
    response = self.postRest(self.modelBaseUrl() + '/groups', json.dumps(data), True)
    print('Response from creating /templates group: ' + str(response.status_code) + ' = ' + response.reason)
    if response.ok:
      print(response.json())
      self.templatesGroupId = response.json()["id"]


    data = { 'link': { 'id': self.rootId, 'name': 'expansions' }}
    response = self.postRest(self.modelBaseUrl() + '/groups', json.dumps(data), True)
    print('Response from creating /expansions group: ' + str(response.status_code) + ' = ' + response.reason)
    if response.ok:
      print(response.json())
      self.expansionsGroupId = response.json()["id"]
      data = { 'type': 'H5T_STD_I32LE', 'value': '0' }
      response = self.putRest(self.modelBaseUrl() + '/groups/' + self.expansionsGroupId + '/attributes/maxindex', json.dumps(data), True)
      print('Response from creating /expansions group attribute maxindex: ' + str(response.status_code) + ' = ' + response.reason)

  def createModel(self):
    #models = self.getExistingModels()
    #modelExists = next((x for x in models if x["title"].lower() == self.modelName.lower()), None)

    #if modelExists:
    #  return 0

    response = self.putRest(self.modelBaseUrl(), None, True)
    if response.status_code == 201:
      self.initializeModel()
      return 0
    elif response.status_code == 409:
      print('Model ' + self.modelName + ' already exists, not creating')
      return 0
    else:
      self.failureReason = 'Model creating (PUT ' + self.modelName + ') failed with HTTP status ' + str(response.status_code)
      return 1

  def deleteModel(self):
    response = self.deleteRest(self.modelBaseUrl(), True)

    print(response)
    return 0


