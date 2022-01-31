"""
import sys
import json
from h5model import h5model

if len(sys.argv) < 3:
  print('Usage: ' + sys.argv[0] + ' ' + '<model name> <expansion sequence>')
  exit(1)

modelName = sys.argv[1]
expansionSequence = int(sys.argv[2])

#print("Getting template expansion " + str(expansionSequence) + " for model '" + modelName + "'")

model = h5model(modelName)
expansion = model.getExpansionFromModel(expansionSequence)

if model.responseStatus < 400:
  print(json.dumps(expansion))
  exit(0)
else:
  print(json.dumps({ "message": model.errorMessage, "status": model.responseStatus }))
  exit(1)
"""