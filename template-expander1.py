import sys
import scipy.stats as stats
import random
from pathlib import Path
import json
from h5utils import h5model

# Validate the arguments, load the common configuration, and the template file.
if len(sys.argv) < 3:
  print('Usage: ' + sys.argv[0] + ' <model> ' + '<template file>', file = sys.stderr)
  exit(1)

with open('/configuration/configuration.json') as f:
  configuration = json.load(f)
#print(configuration)

modelName = sys.argv[1]
print('Expanding a template into model ' + modelName)

templateFile = sys.argv[2]
if (not(templateFile.endswith('json'))):
  templateFile += '.json'

templateFilePath = Path('/templates/' + templateFile)
if not templateFilePath.is_file():
  print("Template '" + sys.argv[2] + "' does not exist", file = sys.stderr)
  exit(1)

print('Expanding template file ' + templateFilePath.as_posix())

with templateFilePath.open() as f:
  template = json.load(f)
#print(template)

# We will need a persistence object specific to the specified model.
model = h5model(modelName)
if not model.rootId:
  print("Model file for '" + modelName + "' not found", file = sys.stderr)
  exit(1)

# Calculate the total neurons needed plus the starting offset and count for each population.
nextIndex = 0
neuronIndexes = {}

neurons = template["neurons"]
for neuron in neurons:
  count = 1
  for dim in neuron["dims"]:
    count *= dim
  neuronIndexes[neuron["name"]] = { "index": nextIndex, "count": count }
  neuron["index"] = nextIndex
  neuron["count"] = count
  nextIndex += count

#print(neuronIndexes)
model.addTemplateToModel(sys.argv[2], template)
if model.responseStatus >= 400:
  print("Unable to add template '" + templateFile + "' to model '" + modelName + "': " + model.errorMessage, file = sys.stderr)
  exit(1)

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
model.addExpansionToModel(sys.argv[2], nextIndex, connections)
if model.responseStatus >= 400:
  print("Unable to add expansion of template '" + templateFile + "' to model '" + modelName + "': " + model.errorMessage, file = sys.stderr)
  exit(1)
