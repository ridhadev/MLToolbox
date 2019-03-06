from multiprocessing import Pool, freeze_support, Queue
import pandas as pd
import os, time
import numpy as np
import glob
FILE_LIST = "W:\\\Group\\Data-Unix\\pau955\\WORK_DIR\\Ridha\\DEV\\01-TOTAL\\01-PROJECTS\\DrillX\\Row_Data_Extraction\\file_analysis\\list_of_input_files.xlsx"

DATA_DIR= "W:\\Entity\\DSO\\FP\\_MTH\\_PERF\\03_DrillX\\06_Data\\03 Raw Exports"
OUTPUT_DIR = "W:\\Group\\Data-Unix\\pau955\\WORK_DIR\\Ridha\\DEV\\01-TOTAL\\01-PROJECTS\\DrillX\\Row_Data_Extraction\\file_analysis\\outputs"

#FILES_DF = pd.read_excel(FILE_LIST)

#files_df = FILES_DF[FILES_DF['EXCLUDE'].isnull()]

#print("Files to read {}".format(files_df ))


###################################################################################################################################################################
def get_seperator(afile):
    sep = None
    with open(os.path.join(DATA_DIR, afile), 'r', encoding="latin-1") as msf:
        l = msf.readline()
        if l.count(',') > l.count(';') :
            sep = ','
        else :
            sep = ';'
    return sep

def read_mnemonics_doc():
    # Mnemonics doc dict
    return pd.read_excel("W:\\Entity\\DSO\\FP\\_MTH\\_PERF\\03_DrillX\\06_Data\\05_Labelised Dataset\\Mnemonics_Library_From_Interact.xlsx").set_index("Channel")


def read_file(filepath):
    curfile = os.path.join(DATA_DIR, filepath)
    sep = get_seperator(curfile)
    curdf = pd.read_csv(curfile, header=[0,1], sep=sep, low_memory=False, encoding='latin-1')
    curdf = curdf.dropna(how='all', axis=0).dropna(how='all', axis=1)
    return curdf

def get_descriptor(aframe):
    return aframe.describe()

def get_index_type(filename):
    if 'time' in filename.lower():
        return 'TIME'
    elif  'depth' in filename.lower():
        return 'DEPTH'

    return "UNKOWN"


def get_columns_doc(frame, global_doc_frame):
    list_of_columns = frame.columns.get_level_values(0).unique()
    items_dict = {}
    for item in list_of_columns:
        if item in global_doc_frame.index:
            items_dict[item] = global_doc_frame.loc[item][["Description", "Measurement"]]
        else:
            items_dict[item] = {"Description": np.nan, "Measurement": np.nan}

    return pd.DataFrame.from_dict(items_dict, orient='index')

def get_index_info(frame, index_type):
    list_of_columns = frame.columns.get_level_values(0).unique()

    if index_type == 'DEPTH':
        depths = ['DEPTH', 'DEPT']
        for depth in depths :
            if depth in list_of_columns:
                dd = {
                    "type": "DEPTH",
                    "min": frame[depth].min(),
                    "max": frame[depth].max(),
                    "range": frame[depth].max() - frame[depth].min(),
                    "std" : np.std(frame[depth])
                }
                return dd

    if index_type == 'TIME':
        times = ["TIME"]
        for tt in times:
            if tt in list_of_columns:
                timeser = pd.to_datetime(frame['TIME', 's'], errors='coerce')
                return {
                    "type" : "TIME",
                    "min": timeser.min(),
                    "max": timeser.max(),
                    "range": timeser.max() - timeser.min(),
                    "std": np.std(timeser.diff()).total_seconds()
                }
    return {
        "type": "UNKNOWN",
        "min": np.nan,
        "max": np.nan,
        "range": np.nan,
        "sqrt": np.nan
    }


def process_data_file(datafile, output_file_path, mnemonics_doc, ignore_if_exist=True):

    try:
        if ignore_if_exist :
            if os.path.exists(output_file_path):
                #print("{} exists already!".format(output_file_path))
                return

        df = read_file(datafile)

        list_of_columns = df.columns.get_level_values(0).unique()

        indextype = get_index_type(datafile)


        indexdf = pd.DataFrame.from_dict(get_index_info(df, indextype), orient='index')

        docdf = get_columns_doc(df, mnemonics_doc)

        dfdesc = get_descriptor(df)

        writer = pd.ExcelWriter(output_file_path, engine='xlsxwriter')

        indexdf.to_excel(writer, sheet_name='index', index=True)
        docdf.to_excel(writer, sheet_name='doc', index=True)
        dfdesc.to_excel(writer, sheet_name='stats', index=True)

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()
    except Exception as ex:
        print(ex)


####################################################################

if __name__ == '__main__':

    files_df = pd.read_excel(FILE_LIST)

    files_df = files_df[files_df['EXCLUDE'].isnull()]

    with_multiprocessing = False
    nbout_start = len(glob.glob(OUTPUT_DIR+ '\\*.xlsx'))

    print("NB xlsx files at start ", nbout_start)

    freeze_support()

    all_mnemonics_doc = read_mnemonics_doc()

    t0 = time.time()

    files_df = pd.read_excel(FILE_LIST)

    files_df = files_df[files_df['EXCLUDE'].isnull()]

    output_file_paths=[(f, os.path.join(OUTPUT_DIR, files_df.loc[f, 'OUTPUT_NAME'] + '.xlsx'), all_mnemonics_doc ) for f in files_df.index.unique()]

    if with_multiprocessing:
        p = Pool(16)
        p.starmap(process_data_file, output_file_paths)
    else:
        for f, output_file_path, dico in output_file_paths:
           try:
               print(f)
               process_data_file(f, output_file_path, dico)
           except Exception as ex:
               print(ex)


    dt = time.time() - t0

    print('*' * 199)

    nbout_diff = len(glob.glob(os.path.join(OUTPUT_DIR , '*.xlsx'))) - nbout_start


    print("Read {} files in {} sec".format(nbout_diff, dt))