import scipy.stats as stats
import random

class modelCompiler:
  h5Model = None
  templateName = ''
  sequence = -1

  template = None
  populations = None
  totalCount = 0

  def __init__(self, h5Model, templateName, sequence):
    self.h5Model = h5Model
    self.templateName = templateName
    self.sequence = sequence

    print('Compiling template ' + templateName + ' into model ' + self.modelName + " as sequence " + str(sequence))
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
      print('Unknown compilation method ' + method)

  def CompileProjection(self):
    connections = []
    for policy in self.template["policies"]:
      sourcePopulation = next((pop for pop in self.populations if pop["name"] == policy["source"]), None)
      targetPopulation = next((pop for pop in self.populations if pop["name"] == policy["target"]), None)
      connectionCount = int(sourcePopulation["count"] * policy["fraction"])

      start = 0
      end = 1000
      scalefactor = 1000
      mu = int(policy["mean"] * scalefactor)
      if mu < 0:
        mu *= -1
        scalefactor *= -1
      sigma = int(policy["sd"] * 1000)
      dist = stats.truncnorm((start - mu) / sigma, (end - mu) / sigma, loc=mu, scale=sigma)
      connectionStrengths = dist.rvs(connectionCount)
      print('Using mu=' + str(mu) + " sigma=" + str(sigma))

      for i in range(connectionCount):
        sourceIndex = random.randrange(sourcePopulation["index"], sourcePopulation["index"] + sourcePopulation["count"])
        targetIndex = random.randrange(targetPopulation["index"], targetPopulation["index"] + targetPopulation["count"])
        print(' Connection: source=' + str(sourceIndex) + ' target=' + str(targetIndex) + ' strength=' + str(connectionStrengths[i] / scalefactor))
        connections.append([sourceIndex, targetIndex, connectionStrengths[i] / scalefactor])

  def ExtractProjectedArea(self, source, target):