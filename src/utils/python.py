
import os
import sys

def add_include_path(path):
    ''' Add package to Python include path

    Add path to "PYTHONPATH" environnement variable

    :param path: Source code path to include
    :return:
    '''
    if "PYTHONPATH" in os.environ:
        if path not in set(os.environ["PYTHONPATH"].split(":")):
            os.environ["PYTHONPATH"] = ":".join([os.environ["PYTHONPATH"], path])
    else:
        os.environ["PYTHONPATH"] = path

    if path not in sys.path:
        sys.path.append(path)