import json


def parse_feelings(context, snapshot):
    feelings = snapshot.feelings
    return json.dumps(feelings)


parse_feelings.field = "feelings"
