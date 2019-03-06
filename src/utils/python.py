
import os
import sys

def add_include_path(path):
    if "PYTHONPATH" in os.environ:
        if path not in set(os.environ["PYTHONPATH"].split(":")):
            os.environ["PYTHONPATH"] = ":".join([os.environ["PYTHONPATH"], path])
    else:
        os.environ["PYTHONPATH"] = path

    if path not in sys.path:
        sys.path.append(path)