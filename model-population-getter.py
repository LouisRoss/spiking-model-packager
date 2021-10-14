import sys
import json
from h5utils import h5model

if len(sys.argv) < 2:
  print('Usage: ' + sys.argv[0] + ' ' + '<model name>')
  exit(1)

modelName = sys.argv[1]

#print("Getting population for model '" + modelName + "'")

model = h5model(modelName)
model.getPopulation()

if model.responseStatus < 400:
  print(json.dumps(model.responseSuccessPayload))
  exit(0)
else:
  print(json.dumps({ "message": model.errorMessage, "status": model.responseStatus }))
  exit(1)