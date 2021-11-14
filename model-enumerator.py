import sys
import json
from h5model import h5model

model = h5model("")
model.getExistingModels()

if model.responseStatus < 400:
  print(json.dumps([x["title"] for x in model.responseSuccessPayload]))
  exit(0)
else:
  print(model.errorMessage, file=sys.stderr)
  exit(model.responseStatus)