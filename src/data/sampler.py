import pandas as pd
import os


from data.excel import DataLoader

from utils.filters import SimpleTextFilter

class DataSampler():

    def  __init__(self, top=None, sampling_fraction=None):
        self.top = top
        self.fraction= min(1, max(0, sampling_fraction))

    @staticmethod
    def get_prefixed_filename(filename, suffix):
        '''
        Get prefixed file name or path of filename with the same extension
        :param filename: File name or path to rename
        :param prefix: Suffix to add
        :return: New file name or path
        '''

        if filename.rfind('.') > -1:
            return filename[:filename.rfind('.')] + suffix + filename[filename.rfind('.'):]
        else:
            return filename + suffix

    def get_sample(self, frame):
        df = frame

        if self.top :
            cur_top = min(frame.shape[0], self.top)
            df = frame.head(cur_top)

        if self.fraction > 0. and self.fraction < 1.:
            df = df.sample(frac = self.fraction)

        return df.copy()


    def resample_excel_file(self, excel_file, excel_reader=None, suffix ='_sampled', sheets_filter=None):

        output_file_name = DataSampler.get_prefixed_filename(excel_file, suffix)

        if excel_file.endswith(".csv"):
            sample_csv_df = pd.read_csv(excel_file)
            self.get_sample(sample_csv_df).to_csv(output_file_name)
            return

        sheets = DataLoader.list_excel_sheets(excel_file)

        writer = pd.ExcelWriter(output_file_name)

        for sheet in sheets:
            sheets = pd.ExcelFile(excel_file).sheet_names

            for sheet in sheets:
                try:
                    if sheets_filter and not sheets_filter.accept(sheet):
                        continue

                    if excel_reader :
                        sampled = self.get_sample(excel_reader(excel_file, sheet))
                    else :
                        sampled = self.get_sample(pd.read_excel(excel_file, sheet_name=sheet))

                    sampled.to_excel(writer, sheet)

                except Exception as ex:
                    print(ex)
                    continue

        writer.save()

if __name__ == '__main__':

    print(os.getcwd())
    csv_file = 'W:\\Group\\Data-Unix\\pau955\\WORK_DIR\\Ridha\\DEV\\PycharmProjects\\MLToolbox\\data\\Iris\\iris_data.csv'

    sampler = DataSampler(sampling_fraction = 0.1)

    sampler.resample_excel_file(csv_file)

    filter = SimpleTextFilter(exclude_filters=['Tags'], include_filters=['ALK_040'])

    reader = lambda file, sheet :  pd.read_excel(file, sheet_name = sheet)

    sampler.resample_excel_file("W:\\Group\\Data-Unix\\pau955\\WORK_DIR\\Ridha\\DEV\\PycharmProjects\\MLToolbox\\data\\FCW_Excel_Data\\ALK\\MyALK_Extraction_FCW_BHP_2018.xlsx", excel_reader = reader, sheets_filter=filter)