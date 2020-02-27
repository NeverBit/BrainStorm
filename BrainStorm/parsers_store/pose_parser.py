import json
from pathlib import Path


def parse_pose(context,snapshot):
    pose = snapshot.pose
    pose_dict = {'translation':snapshot.pose.translation,
                 'rotation':snapshot.pose.rotation
                }
    j = json.dumps(pose_dict)
    print(f'Found POSE: {j}')
    return j
parse_pose.field = "pose"
