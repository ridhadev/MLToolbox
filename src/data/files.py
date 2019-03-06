import pandas as pd
import glob as glob
import re
import fnmatch
import pickle
import os
import platform


##########################################################################################################
#                                                   Utils                                                #
##########################################################################################################

def get_file_size(afile, divide=1000):
    return os.path.getsize(afile) / divide


# Windows support all plateforms, other plateform support only 'create' mode
# mode support 'create', 'access' and 'edit'
def get_file_date(path_to_file, mode='edit'):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
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

def get_short_paths(root_path, all_files):
    return [i[len(root_path):].lstrip('\\') for i in all_files]

######################################################
# Files listing
#
def list_files(root_dir, files_pattern="*.csv|*.xlsx|*.xls", recursive=False, short_path=False, include_dir=False):
    all_files = list_files_in_dir(root_dir, files_pattern, recursive, include_dir)

    if short_path :
        short_files = get_short_paths(root_dir, all_files)
        return short_files

    return all_files

#######################################################################
# Return path depth and file extensions in the list of provided files
# Example opf using the returned values: files_df['EXT'].value_counts() to get count of file extension

def list_files_frame(list_of_files):
    '''
    :param list_of_files: List of files to parse
    :return: path depth and file extensions in the list of provided files
    '''
    f2spec = {f: [len(f.split('\\')), f.split('\\'), f.split('.')[-1].lower()] for f in list_of_files}
    files_df = pd.DataFrame.from_dict(f2spec, orient='index')
    files_df.columns = ['PATH_DEPTH', 'PATHS', 'EXT']
    files_df = files_df.sort_index()
    return files_df


######################################################################
#
#
def list_files_in_dir(directory, files_pattern="*.csv|*.xlsx|*.xls", recursive=False, include_dir=False):
    '''
        List files matching a pattern in a directory.
        The lookup can be recursive into sub directories.
        :param directory Directory to look up to
        :param files_pattern pattern to match seperated by | or a single pattern otherwise. Set to "*" to include all files
        :param recursive Recursive lookup
        :param include_dir List all subdirectories even those not matching the pattern or having no file matching the pattern.
        This could help making sure that directories were processed
        :return List of files with absolute paths if :param short_path is None or relative self._root_dir otherwise
    '''

    files = []

    #pattern = re.compile(files_pattern)
    files_patterns = files_pattern.split('|')
    for f in os.listdir(os.path.join(directory)):
        fpath = os.path.join(directory, f)
        if os.path.isdir(fpath):
            if include_dir:
                files.append(fpath)

            if recursive :
                cur_files = list_files_in_dir(os.path.join(directory, f), files_pattern, recursive)

                if len(cur_files) > 0:
                    files.extend(cur_files)
        else :
            for p in files_patterns:
                if fnmatch.fnmatch(fpath, p):
                    files.append(fpath)

    return files

############################################################################################################
##                                             EXCEL                                                      ##
############################################################################################################


############################################################################################################
# Listing sheet names
#
def list_excel_sheets(excel_file):
    '''
    List excel file sheet names
    '''
    xl = pd.ExcelFile(excel_file)
    return xl.sheet_names


def list_excel_sheets_per_file(excel_files):
    '''
    List set of sheet names for each input excel_files
    :param excel_files : Set of excel sheets to parse
    :return A dictionary of sheet values for every excel file (key)
    '''
    xl_sheets = {}
    for xlf in excel_files:
        try:
            if xlf.endswith('.csv'):
                xl_sheets[xlf] = [os.path.basename(xlf[:-4])]
                continue

            sheets = list_excel_sheets(xlf)
            xl_sheets[xlf] = sheets
        except Exception as ex:
            print('Error at file: ', xlf)
            print(ex)

    return xl_sheets

############################################
# Excel Readers
#
def read_file(abs_file, sheet = None, excel_reader=None, csv_reader=None, file_sheet_seperator="$$"):
    is_csv = fnmatch.fnmatch(abs_file, '*.csv')

    filename = os.path.basename(abs_file)
    filename = filename[:filename.rfind('.')]

    if is_csv:
        if csv_reader:
            df = csv_reader(abs_file)
        else:
            df = pd.read_csv(abs_file)
    else:
        if excel_reader:
            df = excel_reader(abs_file, sheet_name=sheet)
        else:
            df = pd.read_excel(abs_file, sheet_name=sheet)

    fileid = filename
    if sheet :
        fileid += file_sheet_seperator + sheet

    return ExcelData(fileid, df)


def read_files(self, sheets_per_file, excel_reader=None, csv_reader = None):
    parsed_files = {}
    for file, sheets in sheets_per_file.items():
        if len(sheets) > 0:
            for sheet in sheets:
                parsed_files[file + self._file_sheet_seperator + sheet] = self.read_file(file, sheet, excel_reader, csv_reader)
        else :
                parsed_files[file] = self.read_file(file, sheet, excel_reader, csv_reader)
    return parsed_files

##################################################
# Excel multi sheet writer
#
def write_to_excel(output_path, frame_dict, excel_writer = None, file_ext = '.csv', export_index=False) :
    '''
    :param output_path: Output directory path for multi-files export and file path for a single one
    :param frame_dict: Dict of frames with data frame name as key
    :param excel_writer: Lambda function with dataframe argument to write excel or CSV file, one file for each data frame
    :return: Export each data frame in a seperated excel/csv file is a writer is provided, or in one single file otherwise
    with one sheet per data frame.
    '''
    if excel_writer :
        for name, data in frame_dict.items():
            excel_writer(os.path.join(output_path, name + file_ext))
    else :
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(os.path.join(output_path), engine='xlsxwriter')

        for name, data in frame_dict.items():
            # Write each dataframe to a different worksheet.
            data.to_excel(writer, sheet_name=name, index=export_index)

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

###########################################################################################################
def load_pickle_file(pickle_file):
    with open(pickle_file, "rb") as pck_file:
        return pickle.load(pck_file)


def save_to_pickle_file(object_to_save, pickle_file):
    with open(pickle_file, 'wb') as handle:
        pickle.dump(object_to_save, handle, protocol=pickle.HIGHEST_PROTOCOL)

############################################################################################################
#
#
############################################################################################################
class ExcelData():
    '''
    Holds parsed excel file information.
    Keep a clean copy of the read data frame all the time
    '''
    def __init__(self, id, df=None):
        self.__id__ = id

        if df is not None:
            self.__df = df.copy()
        else:
            self.__df = None


    @property
    def df(self):
        return self.__df.copy()

    @df.setter
    def df(self, df):
        self.__df == df.copy()


#######################################################################################################################
#  Tests
#######################################################################################################################
if __name__ == '__main__':
    root_dir = '..\\..\\data\\FCW_Excel_Data'

    import sys
    print(os.getcwd())
    if not os.path.isabs(root_dir):
        abs_root_dir = os.path.abspath(root_dir)
    else :
        abs_root_dir = root_dir


    print("print abs root {}".format(abs_root_dir))


    file_listing = list_files(abs_root_dir, files_pattern="*.xlsx", recursive=True, short_path=False, include_dir=False)

    print(file_listing)

    files_per_sheet = list_excel_sheets_per_file(file_listing)

