import importlib
import json
import pathlib
import sys


registered_parsers = {}

root = globals()['__file__']
root = pathlib.Path(root).absolute()
root = root.parent
sys.path.insert(0, str(root.parent))
for path in root.iterdir():
    if path.name.startswith('_') or not path.suffix == '.py':
        continue
    res = importlib.import_module(
        f'{root.name}.{path.stem}',
        package=root.name)
    for name, val in res.__dict__.items():
        if callable(val) and name.startswith('parse_'):
            registered_parsers[val.field] = val
