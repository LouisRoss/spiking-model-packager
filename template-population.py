import sys
from pathlib import Path
import json
from h5utils import h5model

# Validate the arguments, load the common configuration, and the template file.
if len(sys.argv) < 2:
  print('Usage: ' + sys.argv[0] + ' <model> ' + '[<template1>, <template2>, ...]', file = sys.stderr)
  exit(1)

with open('/configuration/configuration.json') as f:
  configuration = json.load(f)
#print(configuration)

modelName = sys.argv[1]
print('Capturing a template population into model ' + modelName)

templateNames = sys.argv[2:]
population = {}
populationTemplates = []
nextIndex = 0
print('Population has ' + str(len(templateNames)) + ' templates')

# We will need a persistence object specific to the specified model.
model = h5model(modelName)
if not model.rootId:
  print("Model file for '" + modelName + "' not found", file = sys.stderr)
  exit(1)

for templateName in templateNames:
  templateFile = templateName
  if (not(templateFile.endswith('json'))):
    templateFile += '.json'

  templateFilePath = Path('/templates/' + templateFile)
  if not templateFilePath.is_file():
    print("Template '" + sys.argv[2] + "' does not exist", file = sys.stderr)
    exit(1)

  print('Adding template file ' + templateFilePath.as_posix())

  with templateFilePath.open() as f:
    template = json.load(f)
  #print(template)

  # Calculate the total neurons needed plus the starting offset and count for each layer.
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

  populationTemplates.append({'name': templateName, 'indexes': neuronIndexes })

  model.addTemplateToModel(templateName, template)
  if model.responseStatus >= 400:
    print("Unable to add template '" + templateFile + "' to model '" + modelName + "': " + model.errorMessage, file = sys.stderr)
    exit(1)

population["neuroncount"] = nextIndex
population["templates"] = populationTemplates
model.updatePopulationInModel(population)

print("Successfully updated templates " + str(templateNames) + " into model '" + modelName + "'")