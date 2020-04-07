### Adding a new parser
To add a new parser create a new .py file in the ```BrainStorm\parsers_store``` directory.
The name of the file can be anything you like.
Let's examine the existing ```pose_parser.py``` to understand what's important in a parser.
```
import json


def parse_pose(context, snapshot):
    pose_dict = {'translation': snapshot.pose.translation,
                 'rotation': snapshot.pose.rotation
                 }
    return json.dumps(pose_dict)


parse_pose.field = "pose"
```
**The following rules must be kept so the parser can be detected:**
1. The parsnig method MUST start with **"parse_"**
2. A member called ```field``` must be assigned to the method - It should be **any unique identifier (string)** not used by other parsers (Using the name of the parsed field is recommended but not a must)
3. The return object must be a **json**

The parse method recieves 2 parameters: A **'parser context'** object and the **'snapshot'** object to parse.

##### Snapshot parameter
The snapshot object is of type ```SnapshotSlim``` from ```BrainStorm.proto```. You can check this file to see the different fields of the snapshot.

##### Parser Context parameter
The context provides 2 functions to help parsers with binary inputs/outputs:
* ```get_encoded_image``` - Allows the parser to get images raw data as received in the ```server``` and kept in a 'binary blobs' storage.
* ```get_storage_path``` - Allows the parser to get a path to the *output* 'binary blobs' storage where it can save it's results
For reference, the ```col_img_parser.py``` parser utilizes both of the above.

Finally, to run the parser add this line to the end of ```run-pipeline.sh``:
```
docker run -d -v $DATA_DIR:$DATA_DIR -v $RES_DIR:$RES_DIR --network=bsnetwork --name bs_parse_pose_host -e parser_name=*parser_field* bs_parser
```
replacing ```*parser_field*``` with the value in the ```field``` member of the parser.
OR when running from the command line also run a proccess for your new parser:
```
> python -m cortex.parsers run-parser '*parser_field*' 'rabbitmq://127.0.0.1:5672/'
```

### Extra: Visualization of new parsers' results
By following the rules above a parser is automaticlly detected, it's results are saved and accessible to the user via the API (using the cli) or the GUI.

The GUI groups results beloging to the same snapshot together and tries to visualize each one of them.

To allow decoupling of parser additions and their visualization code, a default (simple) visualizer exists which is used for any result without predefined **visualisation plug-in**.

The default plug-in simply *displays the recorded json* returned from the parser, an example for that can be seen for the 'pose' parser.

##### Adding a visualisation plug-in
The GUI is build using flask and the different results plug-ins are each rendered using jinja templates.
The templates are located at ```BrainStorm\templates\results_plugins\```

To add a new plugin create a jinja template in the with the name ```*parser_field*.html``` in the above directory. Note if the name isn't exactly the string saved in the parser method's ```field``` memeber the plug-in won't be recognized.

It's encouraged to review the existing plug-ins in the ```BrainStorm\templates\results_plugins\``` to get an idea of how to make a new template.
