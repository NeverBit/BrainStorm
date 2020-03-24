import json
from pathlib import Path


def parse_feelings(context, snapshot):
    feelings = snapshot.feelings
    j = json.dumps(feelings)
    return j


parse_feelings.field = "feelings"
