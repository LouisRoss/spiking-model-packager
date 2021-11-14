import sys
import json
from h5deployment import h5deployment

if len(sys.argv) < 3:
  print('Usage: ' + sys.argv[0] +  ' <model name>' + ' <deployment name> [server1 server2 ...]')
  exit(1)

modelName = sys.argv[1]
deploymentName = sys.argv[2]
deployment = sys.argv[3:] if len(sys.argv) > 3 else []

#print("Putting deployment '" + deploymentName + "' for model '" + modelName + "'")

modelDep = h5deployment(modelName)
if modelDep.rootId == None:
  modelDep.createModelDeployment()

modelDep.deleteDeploymentFromModel(deploymentName)
modelDep.addDeploymentToModel(deploymentName, deployment)

if modelDep.responseStatus < 400:
  print(json.dumps(modelDep.responseSuccessPayload))
  exit(0)
else:
  print(json.dumps({ "message": model.errorMessage, "status": model.responseStatus }))
  exit(1)