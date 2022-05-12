import scipy.stats as stats
import random

class modelCompiler:
  def __init__(self, h5Model, templateName, sequence):
    self.h5Model = h5Model
    self.templateName = templateName
    self.sequence = sequence

    print('Compiling template ' + templateName + ' into model ' + self.h5Model.modelName + " as sequence " + str(sequence))
    self.template = self.h5Model.getTemplateFromModel(templateName)

    # Calculate the total neurons needed plus the starting offset and count for each population.
    nextIndex = 0
    self.populations = self.template["neurons"]
    for population in self.populations:
      count = 1
      for dim in population["dims"]:
        count *= dim
      population.update({ "index": nextIndex, "count": count })
      nextIndex += count
    self.totalCount = nextIndex

  def Compile(self, method):
    compilationMethod = 'projection'
    if method:
      compilationMethod = method

    if compilationMethod == 'projection':
      self.CompileProjection()

    else:
      print('Unknown compilation method ' + compilationMethod)
      self.errorMessage = 'Unknown compilation method ' + compilationMethod
      self.responseStatus = 503

  def CompileProjection(self):
    connections = []
    for policy in self.template["policies"]:
      sourcePopulation = next((pop for pop in self.populations if pop["name"] == policy["source"]), None)
      targetPopulation = next((pop for pop in self.populations if pop["name"] == policy["target"]), None)

      sourceNeuronCount = int(sourcePopulation["count"] * policy["fraction"])
      sourceNeuronIndexes = random.sample(range(sourcePopulation["index"], sourcePopulation["index"] + sourcePopulation["count"]), sourceNeuronCount)
      for sourceNeuronIndex in sourceNeuronIndexes:
        scalefactor = 1000
        dist = self.get_distribution(policy["mean"], policy["sd"], scalefactor)
        connectionType = self.get_connectionType(policy)

        targetNeuronCount = int(targetPopulation["count"] * policy["fanout"])
        targetNeuronIndexes = random.sample(range(targetPopulation["index"], targetPopulation["index"] + targetPopulation["count"]), targetNeuronCount)
        connectionStrengths = dist.rvs(len(targetNeuronIndexes))
        connectionIndex = 0
        for targetNeuronIndex in targetNeuronIndexes:
          connections.append([sourceNeuronIndex, targetNeuronIndex, connectionStrengths[connectionIndex] / scalefactor, connectionType])
          connectionIndex += 1

    #print(connections)
    self.h5Model.addExpansionToModel(self.sequence, self.templateName, self.totalCount, connections)
    self.responseSuccessPayload = self.h5Model.responseSuccessPayload
    self.errorMessage = self.h5Model.errorMessage
    self.responseStatus = self.h5Model.responseStatus

  def get_distribution(self, mean, sd, scalefactor):
    start = 0
    end = 1000
    mu = int(mean * scalefactor)
    if mu < 0:
      mu *= -1
      scalefactor *= -1
    sigma = int(sd * 1000)
    dist = stats.truncnorm((start - mu) / sigma, (end - mu) / sigma, loc=mu, scale=sigma)
    #connectionStrengths = dist.rvs(connectionCount)
    #print('Using mu=' + str(mu) + " sigma=" + str(sigma))

    return dist

  def get_connectionType(self, policy):
    # Share constants across services in the stack.
    ConnectionType = self.h5Model.settings["constants"]["ConnectionType"]
    connectionType = ConnectionType["Excitatory"]
    if "type" in policy and policy["type"] in ConnectionType:
      connectionType = ConnectionType[policy["type"]]

    return connectionType
