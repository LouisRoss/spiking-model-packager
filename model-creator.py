import sys
import json
from h5utils import h5model

if len(sys.argv) < 2:
  print('Usage: ' + sys.argv[0] + ' ' + '<model name>')
  exit(1)

modelName = sys.argv[1]

print("Creating new model '" + modelName + "'")

model = h5model(modelName)
models = model.createModel()
