import json


def parse_feelings(context, snapshot):
    feelings = snapshot.feelings
    j = json.dumps(feelings)
    return j


parse_feelings.field = "feelings"
