import json


def parse_pose(context, snapshot):
    pose_dict = {'translation': snapshot.pose.translation,
                 'rotation': snapshot.pose.rotation
                 }
    return json.dumps(pose_dict)


parse_pose.field = "pose"
