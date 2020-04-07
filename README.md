# BrainStorm
[![Build Status](https://travis-ci.com/NeverBit/BrainStorm.svg?token=Fs14SrZ67aQ5phGqgwYT&branch=master)](https://travis-ci.com/NeverBit/BrainStorm)
[![codecov](https://codecov.io/gh/NeverBit/BrainStorm/branch/master/graph/badge.svg?token=X6NjL6joF5)](https://codecov.io/gh/NeverBit/BrainStorm)

## Getting Started
First clone or download the repo and enter the directory
```
> git clone https://github.com/NeverBit/BrainStorm.git
> cd BrainStorm
```
Next you should choose from the several options to use the code

### Running with Docker
Inclosed in the repo is the ```run-pipeline.sh``` script which set-ups the main system pipeline
in several docker containers.
The script launches the ```server```, ```parsers```, ```saver```, ```api``` and ```gui``` modules combined with a rabbitmq and postgresql containers all linked to eachothers.
From there, Using the system can be done invoking the ```client``` to upload samples to the system
and using the ```cli``` or a browser (gui is accessible at 127.0.0.1:8080) to see the results.

### Manully usuing the CLI
The project consists of several modlues which should be run as different process to create the entire system.
The runnable modules are:
```
api, cli, client, gui, parsers, saver, server 
```
Each should be run with python's ```-m``` flag like so:
```
python -m BrainStorm.api [command] [args + options]
```
Substitute 'api' with any other module.
To beging exploring the various commands are arguments you can run the module without a command
to get a help page
```
> python -m BrainStorm.api [command] [args + options]
Usage: BrainStorm.api [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  run-server
```

### Using modules in your code
You could also import BrainStorm as a package in your code
``` import BrainStorm```
Without importing sub-modules several main classes and functions are accessible. Including:

* The client's ```upload_sample``` function
* The ```DbBase```, ```Reader``` classes to read from the DB
* The GUI's ```WebServer``` class
* The ```image``` class used to represent images in snapshots
* The ```get_reader``` function used to get readers for .mind files
* The ```registered_parsers``` dictionary holding all parsers in the system
* The ```Snapshot```, ```SnapshotSlim``` classes used to represent snapshots
* The ```run_server``` function to run a snapshot-collecting server
* The ```Saver``` class used to save parser results to the DB


## Extend the system: Parsers
The system uses several stand-alone parsers to retrieve information from the snapshots.
Every parser module is dynamicly located and registered when the system launches.
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
    j = json.dumps(pose_dict)
    return j


parse_pose.field = "pose"
```
**The following rules must be kept so the parser can be detected:**
1. The parsnig method MUST start with **"parse_"**
2. A member called ```field``` must be assigned to the method - It's value should be a string identifing the information the parser is extracting.
3. The return object must be a **json**

The parse method recieves 2 parameters: A **'parser context'** object and the **'snapshot'** object to parse.

##### Snapshot parameter
The snapshot object is of type ```SnapshotSlim``` from ```BrainStorm.proto```. You can check this file to see the different fields of the snapshot.

##### Parser Context parameter
The parser context object's role is to allow parsers intreaction with binary inputs/outputs.
It's 2 functions describe it's abilities:
* ```get_encoded_image``` - Allows the parser to get images raw data as received in the ```server``` and kept in a 'binary blobs' storage.
* ```get_storage_path``` - Allows the parser to get a path to the *output* 'binary blobs' storage where it can save it's results
An example of using the 2 functions can be found in the ```col_img_parser.py```


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
