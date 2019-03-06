import pandas as pd
import glob as glob
import re
import os

#######################################################################################################################
#
#######################################################################################################################
class DataFrameInfo():
    def __init__(self, data_frame):
        self.__df__ = data_frame

#######################################################################################################################
#
#######################################################################################################################
class FilesParser():

    def __init__(self, root_directory):
        self._root_dir = root_directory
        pass

    # List files
    def list_files(self, file_pattern="*", recursive=False, short_path=False, strip_from_path=""):
        '''
        List files matching a pattern in a directory.
        The lookup can be recursive into sub directories.
        '''

        files = []

        for f in glob(os.path.join(self._root_dir, "*")):

            if os.path.isdir(f):
                if recursive :

                    strip = strip_from_path

                    if short_path and len(strip_from_path) == 0:
                        strip = self._root_dir

                    files.extend(self.list_files(os.path.join(self._root_dir, f), file_pattern, recursive, short_path, strip))
            else :
                 for match_file in glob(os.path.join(self._root_dir, file_pattern)):
                    files.append(match_file)

        if short_path and len(strip_from_path) > 0:
            files = [i.lstrip(strip_from_path) for i in files]

        return files

    @staticmethod
    def list_excel_sheets(excel_file):
        xl = pd.ExcelFile(excel_file)
        return xl.sheet_names

########################################################################################################################
#
########################################################################################################################
class ExcelFileReader(object):

    def __init__(self, excel_file_path):
        self.__xl_file__ = excel_file_path

    @staticmethod
    def list_excel_sheets_per_file(excel_files):
        xl_sheets = {}
        for xlf in excel_files:
            try:
                sheets = ExcelFileReader.list_excel_sheets(xlf)
                xl_sheets[xlf] = sheets
            except Exception as ex:
                print('Error at file: ', xlf)
                print(ex)
        return xl_sheets


    def read_files(self, files, include_sheet_regexp =  None, exclude_sheet_regexp = None, file_sheet_sep="$$"):

        file_2_frames = {}

        include_sheet_pat = None
        if include_sheet_regexp:
            include_sheet_pat = re.compile(include_sheet_regexp)

        exclude_sheet_pat = None
        if include_sheet_regexp:
            exclude_sheet_pat = re.compile(include_sheet_regexp)

        for f in files:
            if f.endswith('.csv'):
                file_2_frames[f] = pd.read_csv(f)

            if f.endswith('.xls') or f.endswith('.xlsx'):
                xl = pd.ExcelFile(f)
                for s in xl.sheet_names:
                    if exclude_sheet_pat and exclude_sheet_pat.match(s):
                        continue
                    if include_sheet_pat and (not include_sheet_pat.match(s)):
                        continue
                    