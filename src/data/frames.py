from builtins import bool

import pandas as pd
import numpy as np
from utils.collections import *
from utils.text import *
from collections import OrderedDict, Counter


########################################### Explore    #################################################################

#####################
##      Common     ##
#####################
def get_empty_columns_or_rows(frame, axis=1):
    '''
    axis 0 for columns and 1 for rows
    '''
    return list(frame.count(axis)[frame.count(axis)==0].index)


def get_dimension_info(frame):
    '''
    :param frame:
    :return: Number of rows, columns (and empty ones) global dimension and number of columns per datatype as a dataframe
    '''

    info_dict = OrderedDict()
    ## Size
    nb_rows = frame.shape[0]

    info_dict['rows'] = frame.shape[0]

    info_dict['columns'] = frame.shape[1]
    info_dict['empty_rows'] = len(get_empty_columns_or_rows(frame, axis=1))

    info_dict['empty_columns'] = len(get_empty_columns_or_rows(frame, axis=0))
    info_dict['size'] = frame.shape[0] * frame.shape[1]

    info_dict.update(frame.dtypes.value_counts().to_dict())
    info_df = pd.DataFrame.from_dict(info_dict, orient='index')
    info_df.columns = ['Count']
    return info_df


def compare_dimension_info(before_df, after_df):
    compare_sizes = pd.concat([get_dimension_info(before_df), get_dimension_info(before_df)], axis=1)
    compare_sizes.columns = ['Before', 'After']
    compare_sizes['Diff'] = compare_sizes['After'] - compare_sizes['Before']
    return compare_sizes

#####################
##     Columns     ##
#####################

def get_columns_per_dtype(frame):
    return reverse_dict(frame.dtypes.to_dict())


def get_columns_desc(frame, index_by_dtype=False, sort_by='%fill', ascending_sort=False):
    '''
    :param frame: Frame to describe
    :return: Description of all frame's columns per data type as a dataframe
    '''

    global_desc = pd.DataFrame()

    for t in set(frame.dtypes.values):
        fr = frame.select_dtypes(include=[t]).describe()
        fr.loc['dtype'] = str(t)

        if t == object:
            fr.loc['count_num'] = None
            for c in frame.columns:
                fr.loc['count_num'][c] = pd.to_numeric(frame[c], errors='coerce').dropna().count()

        global_desc = global_desc.join(fr, how='outer')

    col_desc_df = global_desc.T

    if frame.shape[0] > 0:
        col_desc_df['%fill'] = col_desc_df['count'] / frame.shape[0]

    if "unique" in col_desc_df.columns:
        col_desc_df["%unique"] = col_desc_df.apply(
            lambda x: x['unique'] / x['count'] if x['count'] > 0 and x['count'] is not None else 0, axis=1)

    if "count_num" in col_desc_df.columns:
        col_desc_df["%count_num"] = col_desc_df.apply(
            lambda x: x['count_num'] / x['count'] if x['count'] > 0 and x['count'] is not None else 0, axis=1)

    if sort_by:
        col_desc_df = col_desc_df.sort_values(by = sort_by, ascending = ascending_sort)

    if index_by_dtype :
        return col_desc_df.reset_index().set_index(['dtype', 'index']).sort_index()

    return col_desc_df


#
# Outputs two dict oàr dataframes:
# One listing the count of non numeric values per column (values as index in dataframe; better when there are a lot of non-numeric values)
# The second listing the column per non numeric value (column name as index; better with number of non-numeric values smaller than the columns count)
# Example of use :
#       str_values_dict, dd2 = get_non_numeric_values(dataframe, num_candidates)
#       str_values_dict.apply(np.sum, axis=0).sort_values(ascending=False)
#       dd2.apply(np.sum, axis=0).sort_values(ascending=False)

#
# print('Non numeric values per value')
# for nonnum_val in dd2.columns :
#     print(nonnum_val)
#     print(dd2[dd2[nonnum_val].notnull()][nonnum_val])
#
# print('---------------------------------------')
# print('Non numeric values per column')
#
# for nonnum_val in str_values_dict.columns :
#     s= str_values_dict[str_values_dict[nonnum_val].notnull()][nonnum_val]
#     if len(s):
#         print(nonnum_val)
#         print(str_values_dict[str_values_dict[nonnum_val].notnull()][nonnum_val])
def get_non_numeric_values(frame, columns=[], output_as_dataframe=True):
    nonnumeric_values_dict = {}

    reverse_dict = {}

    if not columns:
        candidates = list(frame.columns)
    else:
        candidates = columns

    for c in candidates:
        ss = frame[c]
        nonnumeric_index = ss[pd.to_numeric(ss, errors='coerce').isnull()].index
        nonnumeric_values_dict[c] = ss.loc[nonnumeric_index].value_counts().to_dict()
        for k, v in nonnumeric_values_dict[c].items():
            if k in reverse_dict.keys():
                reverse_dict[k].update({c: v})
            else:
                reverse_dict[k] = {c: v}

    if output_as_dataframe:
        nonnumeric_values_dict = pd.DataFrame.from_dict(nonnumeric_values_dict)
        reverse_dict = pd.DataFrame.from_dict(reverse_dict)

    return nonnumeric_values_dict, reverse_dict


###############################
#
###################################
def get_misfilled_columns(frame, desc_frame, threshold_col = "%filled", threshold = 0.75, dtypes=[]) :
    if dtypes:
        return list(desc_frame[desc_frame[threshold_col] < threshold].index).select_dtypes(include=dtypes)
    else:
        return list(desc_frame[desc_frame[threshold_col] < threshold].index)

def get_numeric_candidates(frame, desc_frame, threshold_col = "%count_num", threshold = 0.75, only_obj_columns=True) :
    candidates = list(desc_frame[desc_frame[threshold_col] >= threshold].index)
    if only_obj_columns :
        candidates = list(set(candidates) - set(frame.select_dtypes(exclude=[np.object]).columns))
    return candidates

def is_boolean_serie(aserie,
                     true_labels=('y', 'yes', 'ok', 'o', 'true', '1'),
                     false_labels=['n', 'no', 'ko', 'nok', 'false', '0']
                     ):
    values = set(aserie.dropna().values)
    if len(values) == 2:
        v1 = str(values.pop()).lower()
        v2 = str(values.pop()).lower()
        print(v1, v2)
        return ((v1 in true_labels) and (v2 in false_labels)) or ((v2 in true_labels) and (v1 in false_labels))

    return False


def get_boolean_candidates(frame, desc_frame, threshold_col = "%count_num", threshold = 0.75, only_obj_columns=True) :

    candidates = list(desc_frame[desc_frame['unique'] == 2].index)

    if only_obj_columns :
        candidates = list(set(candidates) - set(frame.select_dtypes(include=[np.object]).columns))

    return [c for c in candidates if is_boolean_serie(frame[c])]

########################################### Clean/edit #################################################################

#####################
##     Common      ##
#####################

## NaN and drop columns
def setna(frame, values, verbose=True):
    if verbose:
        print('Total number of Nan before: ', sum(frame.isnull().sum().values))

    result = frame.replace(values, np.nan)

    if verbose:
        print('Total number of Nan after : {} (diff of {}) '.format(sum(result.isnull().sum().values),
                                                                    sum(result.isnull().sum().values) - sum(
                                                                        frame.isnull().sum().values)))
    return result

def drop_empty_rows_and_columns(frame, columns=True, rows=True, verbose=True):
    '''
    Drop empty rows and/or columns
    '''
    if verbose:
        print('Before removing (rows, columns) shape was', frame.shape)

    dff = frame

    if columns:
        dff = dff.dropna(axis=1, how='all')

    if rows:
        dff = dff.dropna(axis=0, how='all')

    if verbose:
        removed_columns = set(frame.columns) - set(dff.columns)
        print('After removing (rows, columns) shape was', dff.shape)
        if len(removed_columns) > 0:
            print('Removed columns: ', removed_columns)

    return dff


#####################
##     Columns     ##
#####################

# Drop misfilled columns

def drop_misfilled_columns(frame, desc_frame, threshold_col = "%fill", threshold = 0.75, verbose=True) :
    columns_to_drop = get_misfilled_columns(frame, desc_frame, threshold_col=threshold_col, threshold=threshold)
    if verbose :
        print("Misfilled columns : ", columns_to_drop)
    else :
        print("No misfilled columns to drop")

    if columns_to_drop :
        return frame.drop(columns=columns_to_drop)

    return frame


### Handling data type and conversion

# Numeric
def convert_to_numeric(frame, columns, verbose=True):
    if verbose:
        print('Before conversion')
        print(dict(Counter(frame.dtypes.values)))

    for c in columns:

        if c not in frame.columns:
            raise Exception('Unknown column {}', c)

        #frame[c] = frame[c].apply(pd.to_numeric, errors="ignore", downcast="integer")
        frame.loc[:, c] = pd.to_numeric(frame[c], errors='coerce', downcast="integer")

    if verbose:
        print('After conversion')
        print(dict(Counter(frame.dtypes.values)))

    return frame

## Boolean: Cannot really convert to boolean if the column has NaN values (interpreted as True)
## so convert to 'category' dtype
def convert_to_boolean(frame, columns=[],
                     true_labels=('y', 'yes', 'ok', 'o', 'true', '1'),
                     false_labels=['n', 'no', 'ko', 'nok', 'false', '0'],
                     verbose=True
                     ):

    is_empty = len(columns) == 0
    cols = columns
    if is_empty:
        cols = frame.columns
    boolean_map = dict(zip(true_labels, len(true_labels) * [True]))

    boolean_map.update(dict(zip(false_labels, len(false_labels) * [False])))

    if verbose:
        print('Before conversion')
        print(dict(Counter(frame.dtypes.values)))

    converted_columns = []
    for c in cols:
        if is_empty:
            if is_boolean_serie(frame[c]) :
                frame[c] = frame[c].map(boolean_map).astype('category')
                converted_columns.append(c)
        else :
            frame[c] = frame[c].map(boolean_map).astype('category')
            converted_columns.append(c)

    if verbose:
        print('After conversion')
        print(dict(Counter(frame.dtypes.values)))
        print('Mapped columns: ', converted_columns)

    return frame

## Transform

def preprocess_columns_per_dtype(
        frame,
        mapper,
        exclude_columns=[]):

    for k, v in mapper.items():

        selected_columns = frame.select_dtypes(include=k)

        for c in selected_columns:
            if c in exclude_columns:
                continue

            frame.loc[:, c] = frame[c].map(v, na_action='ignore')

    return frame



def normalize_text_columns(text):
    if pd.isnull(text):
        return text
    return remove_repetitive_chars(str(text).lower().strip(), ' ')


## Merge columns

# Combine in given order the provided columns (NaN values of the first columns are replaced by the second columns' valid value)
#
def combine_columns(frame, ordered_columns):
    print('NOT TESTED YET')
    new_serie = frame[ordered_columns[0]]
    for c in range(1, len(ordered_columns)):
        new_serie = new_serie.combine_first(frame[ordered_columns[c]])
    return new_serie

#
#
#
def fillna(frame, columns, method='mean'):
    for c in columns:
        if method == 'mean':
            frame.loc[:, c] = frame[c].fillna(np.mean(frame[c].dropna()))
        if method == 'median':
            frame.loc[:, c] = frame[c].fillna(np.median(frame[c].dropna()))
        if method == 'most':
            frame.loc[:, c] = frame[c].value_counts().sort_values(ascending=False).index[0]
    return frame