import pandas as pd
import datetime
import os
from files.metadata import get_file_size, get_file_date

########################################################################################################################
#
#
def list_files_indir(dir, files_only=True, dir_only=False, absolute_path=False):
    results = []

    def add_absolute_path_if_needed(results):
        if absolute_path:
            return [os.path.join(dir, r) for r in results]
        return results

    if files_only and dir_only :
        return add_absolute_path_if_needed(list(os.listdir(dir)))

    if files_only :
        return add_absolute_path_if_needed([f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))])

    if dir_only:
        return add_absolute_path_if_needed([f for f in os.listdir(dir) if os.path.isdir(os.path.join(dir, f))])

    return add_absolute_path_if_needed( list(os.listdir(dir)) )

########################################################################################################################
#
#
class FilesProcessStatus:
    '''

    '''
    def __init__(self, input2output_files):
        self.files_frame = pd.DataFrame.from_dict(input2output_files, orient='index')
        self.files_frame.columns = ['Ouput']

    def get_files_metadata(self):
        self.files_frame["INPUT_SIZE"] = self.files_frame.index.map(get_file_size)
        self.files_frame["INPUT_CREATE_DATE"] = self.files_frame.index.map( lambda fpath : datetime.datetime.fromtimestamp(get_file_date(fpath, mode='create')))
        self.files_frame["INPUT_EDIT_DATE"] = self.files_frame.index.map( lambda fpath : datetime.datetime.fromtimestamp(get_file_date(fpath, mode='edit') ))

        self.files_frame["OUTPUT_SIZE"] = self.files_frame.Ouput.apply(get_file_size)
        self.files_frame["OUTPUT_CREATE_DATE"] = self.files_frame.Ouput.apply(
            lambda fpath: datetime.datetime.fromtimestamp(get_file_date(fpath, mode='create')) if os.path.exists(fpath) else pd.NaT)
        self.files_frame["OUTPUT_EDIT_DATE"] = self.files_frame.Ouput.apply(
            lambda fpath: datetime.datetime.fromtimestamp(get_file_date(fpath, mode='edit')) if os.path.exists(fpath) else pd.NaT)

        return self.files_frame


    def get_parsing_status(self, row):
        '''

        :param row:
        :return:
        '''
        if pd.isnull(row.OUTPUT_EDIT_DATE):
            return "MISSING"

        if row.OUTPUT_EDIT_DATE < row.INPUT_EDIT_DATE:
            return "OUT_OF_DATE"
        else:
            return "UP_TO_DATE"


    def compute_file_status(files_frame=None):
        '''
            Get the parsing status: "MISSING" if the file was not parsed yet, "UP_TO_DATE" if the edition time of output file is later than the input one;  "OUT_OF_DATE" otherwise
            :param row:
            :return:
        '''
        def get_parsing_status(row):
            if pd.isnull(row.OUTPUT_EDIT_DATE):
                return "MISSING"

            if row.OUTPUT_EDIT_DATE < row.INPUT_EDIT_DATE:
                return "OUT_OF_DATE"
            else:
                return "UP_TO_DATE"

        files_frame["STATUS"] = files_frame.apply(lambda x: get_parsing_status(x), axis=1)
        return files_frame

    def get_missing_input_files(self, output_dir):
        '''
        List files in the output directory and not listed as output file in the initial dataframe.
        Either the file is not supposed to be an output one; or it is one that was done in the past and the original parsed file is missing or renamed.
        :param output_dir:
        :return:
        '''
        files = list_files_indir(output_dir, absolute_path=True)
        return set(files) - set(self.files_frame.Ouput.values)

########################################################################################################################
#
#
#
if __name__ == '__main__':
    df = pd.read_csv("W:\\Group\\Data-Unix\\pau955\\WORK_DIR\\Ridha\\DEV\\PycharmProjects\\MLToolbox\\data\\TestFiles\\files_status_compare.csv", sep=',')

    df_dict= dict(zip(df['FilePath'].values, df['Output'].values))
    fps = FilesProcessStatus(df_dict)
    print(fps.get_missing_input_files("W:\\Group\\Data-Unix\\pau955\\WORK_DIR\\Ridha\\DEV\\01-TOTAL\\01-PROJECTS\\DrillX\\Row_Data_Extraction\\resampled_uc2"))

    #outfr = fps.get_files_metadata()
    #fr = FilesProcessStatus.compute_file_status(outfr)
    #print(fr)