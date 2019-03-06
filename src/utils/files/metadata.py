import datetime
import platform
import os



def get_file_size(afile, divide=1000):
    if not os.path.exists(afile):
        return None
    return os.path.getsize(afile) / divide


# Windows support all plateforms, other plateform support only 'create' mode
# mode support 'create', 'access' and 'edit'
def get_file_date(path_to_file, mode='edit'):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if not os.path.exists(path_to_file):
        return None

    if platform.system() == 'Windows':
        if mode == 'create':
            return os.path.getctime(path_to_file)
        elif mode == 'access':
            return os.path.getatime(path_to_file)
        else:
            return os.path.getmtime(path_to_file)

    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def get_files_metadata(file_paths):
    metadata_dict = {}

    metadata_dict['SIZE_Ko'] = [ get_file_size(fpath) for fpath in file_paths]
    metadata_dict['CREATE_DATE'] = [ datetime.datetime.fromtimestamp(get_file_date(fpath), mode='create')  for fpath in file_paths]
    metadata_dict['EDIT_DATE'] = [ datetime.datetime.fromtimestamp(get_file_date(fpath), mode='edit')  for fpath in file_paths]

    return metadata_dict