import sys
import json
from h5utils import h5model

if len(sys.argv) < 2:
  print('Usage: ' + sys.argv[0] + ' ' + '<model name>')
  exit(1)

modelName = sys.argv[1]

model = h5model(modelName)
model.createModel()
if model.responseStatus >= 400:
  print("Unable to create model '" + modelName + "': " + model.errorMessage, file = sys.stderr)
  exit(1)

print(model.responseSuccessPayload)