import sys
import scipy.stats as stats
import random
import json
from h5utils import h5model

if len(sys.argv) < 3:
  print('Usage: ' + sys.argv[0] + ' <model> ' + '<template file>')
  exit(1)

f = open('/configuration/configuration.json')
configuration = json.load(f)
print(configuration)

modelName = sys.argv[1]
print('Expanding a template into model ' + modelName)

templateFile = sys.argv[2]
if (not(templateFile.endswith('json'))):
  templateFile += '.json'

templateFilePath = '/templates/' + templateFile
print('Expanding template file ' + templateFilePath)

f = open(templateFilePath)
template = json.load(f)
#print(template)

model = h5model(modelName)
model.addTemplateToModel(sys.argv[2], template)

nextIndex = 0
neuronIndexes = {}

neurons = template["neurons"]
for neuron in neurons:
  count = 1
  for dim in neuron["dims"]:
    count *= dim
  neuronIndexes[neuron["name"]] = { "index": nextIndex, "count": count }
  nextIndex += count

#print(neuronIndexes)

connections = []
for policy in template["policies"]:
  sourceNeuron = neuronIndexes[policy["source"]]
  targetNeuron = neuronIndexes[policy["target"]]
  connectionCount = int(sourceNeuron["count"] * policy["fraction"])

  start = 0
  end = 1000
  mu = int(policy["mean"] * 1000)
  sigma = int(policy["sd"] * 1000)
  dist = stats.truncnorm((start - mu) / sigma, (end - mu) / sigma, loc=mu, scale=sigma)
  connectionStrengths = dist.rvs(connectionCount)

  for i in range(connectionCount):
    sourceIndex = random.randrange(sourceNeuron["index"], sourceNeuron["index"] + sourceNeuron["count"])
    targetIndex = random.randrange(targetNeuron["index"], targetNeuron["index"] + targetNeuron["count"])
    connections.append([sourceIndex, targetIndex, connectionStrengths[i] / 1000.0])

#print(connections)
model.addExpansionToModel(sys.argv[2], connections)
