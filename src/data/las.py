import re
import numpy as np
import pandas as pd
from data.frames import *


############################################################################################
#
############################################################################################
def read_las_file(las_file):
    features = []
    start_data = False
    data = []
    nb_features = 0
    with open(las_file, 'r') as f:
        l = f.readline()
        while l:
            l = f.readline().strip()

            if l.startswith('#'): # skip commented lines
                continue

            if l.startswith('XREF'): # List of features
                features.append(l.split(' ')[1])
                nb_features += 1

            if l.startswith('~A'): # start data section listing
                start_data = True
                continue

            if start_data :
                cur_data = re.sub(' +', ' ', l.strip()).split(' ')
                # print(cur_data)
                if len(cur_data) >= nb_features:
                    data.append(cur_data[:nb_features])
    return features, data

############################################################################################
#
############################################################################################
def read_las_file_as_dataframe(las_file, index_feature_order= None, date_feature_order= None, na_value=-999.25):

    las_features, las_data = read_las_file(las_file)

    las_array = np.array(las_data)

    df = pd.DataFrame(las_array, columns=las_features)

    if date_feature_order is not None :
        time_feature = las_features[date_feature_order]
        df[time_feature] = pd.to_datetime(df[time_feature], format='%d/%m/%Y-%H:%M:%S')

    if index_feature_order is not None:
        index_feature = las_features[index_feature_order]
        df = df.set_index(index_feature).sort_index()

    convert_to_numeric(df, df.columns)

    if na_value :
        df = df.replace(na_value, np.nan)

    return df