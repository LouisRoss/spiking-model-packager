import sys
import json
import requests

class h5Rest:
  modelName = ""
  persistHost = ""
  persistPort = ""
  persistBaseDomain = ""
  modelBaseUrl = ""
  modelDomain = ""
  headers = { 'Accept': 'application/json' }
  configuration = None


  def __init__(self, modelName):
    self.modelName = modelName
    self.failureReason = ""

    f = open('/configuration/configuration.json')
    self.configuration = json.load(f)

    self.persistHost = self.configuration["services"]["modelPersist"]["host"]
    self.persistPort = self.configuration["services"]["modelPersist"]["port"]
    self.persistBaseDomain = self.configuration["services"]["modelPersist"]["basedomain"]

    self.modelBaseUrl = self.persistHost + ":" + self.persistPort
    self.modelDomain = self.modelName + '.' + self.persistBaseDomain

  def getRest(self, url, addHost=False):
    fullUrl = self.modelBaseUrl + url
    fullUrl = fullUrl + '?host=' + self.modelDomain if addHost else fullUrl
    #print('GETting from URL: ' + fullUrl)

    response = requests.get(fullUrl, headers=self.headers)
    #print(response)
    #print()
    return response

  def putRest(self, url, data, addHost=False):
    fullUrl = self.modelBaseUrl + url
    fullUrl = fullUrl + '?host=' + self.modelDomain if addHost else fullUrl
    print('PUTting to URL: ' +fullUrl)

    response = requests.put(fullUrl, headers=self.headers, data=data)
    #print(response)
    #print()
    return response

  def postRest(self, url, data, addHost=False):
    headers = self.headers
    headers['host'] = self.modelDomain
    fullUrl = self.modelBaseUrl + url
    print('POSTting to URL: ' + fullUrl)

    response = requests.post(fullUrl, headers=headers, data=data)
    #print(response)
    #print()
    return response

  def deleteRest(self, url, addHost=False):
    fullUrl = self.modelBaseUrl + url
    fullUrl = fullUrl + '?host=' + self.modelDomain if addHost else fullUrl
    print('DELETEing URL: ' + fullUrl)

    response = requests.delete(fullUrl, headers=self.headers)
    #print(response)
    #print()
    return response

  def getRestStep(self, url, key, addHost=False):
    response = self.getRest(url, addHost)
    hrefElement = next((x for x in response["hrefs"] if x["rel"] == key), None)
    return hrefElement

