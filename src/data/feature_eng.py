from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np

## Todo  Remove outliers
## Todo

#########################################################################################################################################
# Normalize Numerical Data
#########################################################################################################################################
#
#
# Equivalent to custom_minmax_scale(xl, scale_func=lambda aserie: MinMaxScaler().fit_transform(aserie.values.reshape(-1, 1)))
def minmax_scale(frame, columns=[], inplace=False):
    return custom_minmax_scale(frame, scale_func=lambda aserie: MinMaxScaler().fit_transform(aserie.values.reshape(-1, 1)), columns= columns, inplace=inplace)


def custom_minmax_scale(frame, scale_func, columns=[], inplace=False):
    num_columns = columns
    if not num_columns:
        num_columns = frame.select_dtypes(include=[np.float]).columns

    minmax_df = frame if inplace else pd.DataFrame(index=frame.index)

    for c in num_columns:
        minmax_df.loc[:, c] = scale_func(frame[c])

    return minmax_df



def detect_outliers(frame, columns = []):
    pass

def drop_outliers(frame, columns = []):
    pass