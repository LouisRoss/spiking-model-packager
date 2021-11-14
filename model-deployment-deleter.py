import sys
import json
from h5deployment import h5deployment

if len(sys.argv) < 3:
  print('Usage: ' + sys.argv[0] +  ' <model name>' + ' <deployment name>')
  exit(1)

modelName = sys.argv[1]
deploymentName = sys.argv[2]

#print("Deleting deployment '" + deploymentName + "' from model '" + modelName + "'")

modelDep = h5deployment(modelName)
if modelDep.rootId == None:
  modelDep.createModelDeployment()

modelDep.deleteDeploymentFromModel(deploymentName)

if modelDep.responseStatus < 400:
  print(json.dumps(modelDep.responseSuccessPayload))
  exit(0)
else:
  print(json.dumps({ "message": modelDep.errorMessage, "status": modelDep.responseStatus }), file=sys.stderr)
  exit(1)