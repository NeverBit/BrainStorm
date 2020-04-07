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
The deployment script launches the ```server```, ```parsers```, ```saver```, ```api``` and ```gui``` modules combined with a rabbitmq and postgresql containers all linked to eachothers.
```
> ./run-pipeline.sh     # sudo might be required for docker
```
Then use the ```client```, ```cli``` as described in the *Manully running from the commandline* or browser to 127.0.0.1:8080 to see the GUI.

### Manully running from the commandline
Begin by activating the virtual enviroment:
```
> ./scripts/install.sh
> source .env/bin/activate
```
Now you can run any of the available modules which construct the entire system:
```
api, cli, client, gui, parsers, saver, server 
```
Each should be run with python's ```-m``` flag like so:
```
> python -m BrainStorm.api [command] [args + options]
```
Substitute 'api' with any other module.
To begin exploring the various commands and arguments you can run the module without a command
to get the help page:
```
> python -m BrainStorm.api
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
* The ```Reader``` classes to read from the DB
* The GUI's ```WebServer``` class
* The ```image``` class used to represent images in snapshots
* The ```get_reader``` function used to get readers for .mind files
* The ```registered_parsers``` dictionary holding all parsers in the system
* The ```Snapshot```, ```SnapshotSlim``` classes used to represent snapshots
* The ```run_server``` function to run a snapshot-collecting server
* The ```Saver``` class used to save parser results to the DB



## Extend the system: Parsers
The system uses several stand-alone parsers to retrieve information from the snapshots.
Every parser module is automatically discovered and loaded when the system launches.

Please refer to [Adding a parser](adding_a_parser.md) for the instructions.
