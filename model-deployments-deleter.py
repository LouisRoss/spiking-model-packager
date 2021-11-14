import sys
import json
from h5deployment import h5deployment

if len(sys.argv) < 2:
  print('Usage: ' + sys.argv[0] +  ' <model name>')
  exit(1)

modelName = sys.argv[1]

#print("Deleting deployments from model '" + modelName + "'")

modelDep = h5deployment(modelName)
if modelDep.rootId == None:
  modelDep.createModelDeployment()

modelDep.deleteModelDeployments()

if modelDep.responseStatus < 400:
  print(json.dumps(modelDep.responseSuccessPayload))
  exit(0)
else:
  print(json.dumps({ "message": modelDep.errorMessage, "status": modelDep.responseStatus }), file=sys.stderr)
  exit(1)