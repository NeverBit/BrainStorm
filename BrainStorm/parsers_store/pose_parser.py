import json


def parse_pose(context, snapshot):
    pose_dict = {'translation': snapshot.pose.translation,
                 'rotation': snapshot.pose.rotation
                 }
    j = json.dumps(pose_dict)
    return j


parse_pose.field = "pose"
