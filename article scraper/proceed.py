import json

with open("catdata.json", "r") as f:
    catdata = json.load(f)

print(catdata["payload"].keys())