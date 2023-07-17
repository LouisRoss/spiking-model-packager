import sys
import json
from h5model import h5model

if len(sys.argv) < 3:
  print('Usage: ' + sys.argv[0] +  ' <model name>' + ' <template sequence> [[connection1] [connection2] ...]')
  exit(1)

modelName = sys.argv[1]
templateSequence = int(sys.argv[2])
expansion = sys.argv[3] if len(sys.argv) > 3 else ['']

#print("Putting expansion '" + str(templateSequence) + "' for model '" + modelName + "'")
jsonExpansion = json.loads(expansion)
neuronCount = int(jsonExpansion["neuroncount"])
synapses = jsonExpansion["synapses"]
print('Neuron count: ' + str(neuronCount) + ', synapses:')
print(synapses)

model = h5model(modelName)
if not model.rootId:
  print("Model file for '" + modelName + "' not found", file = sys.stderr)
  exit(1)

model.addExpansionToModel(templateSequence, 'computed', neuronCount, synapses)

if model.responseStatus < 400:
  print(json.dumps(model.responseSuccessPayload))
  exit(0)
else:
  print(json.dumps({ "message": model.errorMessage, "status": model.responseStatus }))
  exit(1)
