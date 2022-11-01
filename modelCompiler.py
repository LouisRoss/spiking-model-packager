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

  def Compile(self):
    defaultCompilationMethod = 'projection'
    if 'method' in self.template:
      defaultCompilationMethod = self.template['method']

    connections = []
    for policy in self.template["policies"]:
      compilationMethod = defaultCompilationMethod
      if 'method' in policy:
        compilationMethod = policy['method']

      if compilationMethod == 'projection':
        connections.extend(self.CompileProjection(policy))

      elif compilationMethod == 'unique':
        connections.extend(self.CompileUnique(policy))

      elif compilationMethod == 'explicit':
        connections.extend(self.CompileExplicit(policy))

      else:
        print('Unknown compilation method ' + compilationMethod)
        self.errorMessage = 'Unknown compilation method ' + compilationMethod
        self.responseStatus = 503
        return

    #print(connections)
    self.h5Model.addExpansionToModel(self.sequence, self.templateName, self.totalCount, connections)
    self.responseSuccessPayload = self.h5Model.responseSuccessPayload
    self.errorMessage = self.h5Model.errorMessage
    self.responseStatus = self.h5Model.responseStatus

  def CompileProjection(self, policy):
    """ A policy was found that should be compiled using the 'projection' method.
        In 'projection', we project a random subset of the source population to a
        random subset of the target population.  Required fields in a 'projection'
        policy are 'fraction', 'fanout', 'mean', and 'sd'.
        'fraction' specifies the fraction of source neurons connected.
        'fanout' specifies the fraction of target neurons that each connected source neuron projects to.
        'mean' and 'sd' specify the random distribution used to make connection strengths.
    """
    sourcePopulation = next((pop for pop in self.populations if pop["name"] == policy["source"]), None)
    targetPopulation = next((pop for pop in self.populations if pop["name"] == policy["target"]), None)

    sourceNeuronCount = int(sourcePopulation["count"] * policy["fraction"])
    sourceNeuronIndexes = random.sample(range(sourcePopulation["index"], sourcePopulation["index"] + sourcePopulation["count"]), sourceNeuronCount)

    connections = []
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

    return connections

  def CompileUnique(self, policy):
    """ A policy was found that should be compiled using the 'unique' method.
        In 'unique', we perform a one-to-one connection between the source and target
        populations.  If the populations are not the same size, only make as many
        connections as the size of the smaller population.
        There are no expected fields in the policy other than 'source' and 'target'.
        Often, a 'type' method of 'Attention' is typical, but unique compilations can
        be made with other synapse types.
    """
    sourcePopulation = next((pop for pop in self.populations if pop["name"] == policy["source"]), None)
    targetPopulation = next((pop for pop in self.populations if pop["name"] == policy["target"]), None)
    connectionType = self.get_connectionType(policy)

    connectionCount = min(sourcePopulation['count'], targetPopulation['count'])
    sourceNeuronIndex = sourcePopulation['index']
    targetNeuronIndex = targetPopulation['index']

    connections = []
    for i in range(connectionCount):
        connections.append([sourceNeuronIndex, targetNeuronIndex, 1.0, connectionType])
        sourceNeuronIndex += 1
        targetNeuronIndex += 1

    return connections

  def CompileExplicit(self, policy):
    """ A policy was found that should be compiled using the 'explicit' method.
        In 'explicit', the actual wiring is in the policy's 'expansion' field,
        which must be an array of 3-elemnt arrays:
        'expansion': [
          [source, target, stength],
          [source, target, stength],
          ...
        ]

        The policy's 'source' and 'target' fields must name populations that already
        exist, and are relative to that population's 'index' element.
        The 'type' field may be provided in the policy to override the default.
        In any case, 'type' specifies the connection type for all synapses in the
        expansion for this policy.
    """
    sourcePopulation = next((pop for pop in self.populations if pop["name"] == policy["source"]), None)
    targetPopulation = next((pop for pop in self.populations if pop["name"] == policy["target"]), None)
    connectionType = self.get_connectionType(policy)

    expansion = []
    if 'expansion' in policy:
      expansion = policy['expansion']

    sourceNeuronIndex = sourcePopulation['index']
    targetNeuronIndex = targetPopulation['index']

    connections = []
    for connection in expansion:
        connections.append([sourceNeuronIndex + connection[0], targetNeuronIndex + connection[1], connection[2], connectionType])

    return connections

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
