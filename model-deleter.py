import sys
import json
from h5model import h5model
from h5deployment import h5deployment

if len(sys.argv) < 2:
  print('Usage: ' + sys.argv[0] + ' ' + '<model name>')
  exit(1)

modelName = sys.argv[1]

modelDep = h5deployment(modelName)
if modelDep.rootId:
  modelDep.deleteModelDeployments()

model = h5model(modelName)
if not model.rootId:
  print("Model file for '" + modelName + "' not found", file = sys.stderr)
  exit(1)

models = model.deleteModel()
if model.responseStatus >= 400:
  print("Unable to delete model '" + modelName + "': " + model.errorMessage, file = sys.stderr)
  exit(1)

print(model.responseSuccessPayload)