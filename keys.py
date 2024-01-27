import json

with open("keys.json") as keys:
    keys = json.loads(keys.read())
    tbaKey = keys["tbaKey"]
    discordKey = keys["discordKey"]