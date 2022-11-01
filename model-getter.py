import sys
import json
from h5model import h5model

if len(sys.argv) < 2:
  print('Usage: ' + sys.argv[0] + ' ' + '<model name>')
  exit(1)

modelName = sys.argv[1]

#print("Getting for model '" + modelName + "'")

model = h5model(modelName)
model.getPopulation()

if model.responseStatus >= 400:
  print(json.dumps({ "message": model.errorMessage, "status": model.responseStatus }))
  exit(1)

populations = []
if "templates" in model.responseSuccessPayload:
    populations = [{ "template": template["template"], "population": template["population"] } for template in model.responseSuccessPayload["templates"]]

for population in populations:
    population["rawtemplate"] = model.getTemplateFromModel(population["template"])

if model.responseStatus < 400:
  print(json.dumps(populations))
  exit(0)
else:
  print(json.dumps({ "message": model.errorMessage, "status": model.responseStatus }))
  exit(1)
