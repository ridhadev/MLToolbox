import pandas as pd
from collections import Counter
from utils.text import *


########################################### Explore    #################################################################

# Occurence count of each column header
def get_column_labels_count(frame, duplicated_only=True):
    c = Counter(frame.columns)
    col_counts_df = pd.DataFrame.from_dict(dict(c.items()), orient='index')
    col_counts_df.columns = ['count']

    if duplicated_only:
        return col_counts_df[col_counts_df["count"] > 1]

    return col_counts_df

# Check whether there is a duplicated column or not
def has_duplicated_labels(frame, axis=1, verbose=False):
    has = get_duplicated_labels(frame, axis=axis).shape[0] > 0
    if has:
        print(get_duplicated_labels(frame))
    return has

# return duplicated columns
def get_duplicated_labels(frame, axis=1):
    if axis == 1:
        return frame.columns[frame.columns.duplicated()]
    return frame.index[frame.index.duplicated()]


########################################### Clean/edit #################################################################

# Normalized column headers: Capital letter, remove special chars according to a provided map, replace
def get_clean_header_label(column_name, default_name='UNNAMED', char_map = None):
    if column_name is None or column_name.strip() == '':
        return default_name
    clean_label = remove_repetitive_chars(remove_special_chars(column_name), ' ').strip().replace(' ', '_').upper()
    if char_map:
        return replace_special_chars(clean_label, char_map)

    return char_map


def get_clean_header_labels(header, cleaner_lambda = lambda x : get_clean_header_label(x) ):
    if isinstance(header, pd.DataFrame):
        header.columns = get_clean_header_labels(header.columns, cleaner_lambda)
        return header

    return [cleaner_lambda(col) for col in header]


def merge_headers(frame, start_row, end_row, ffill=True, joiner_string=' '):
    '''
    Merge the rows from start_row to _end_row (inclusive) and set them as column header then drop those rows.
    This is for files where the header may be specified across several rows (category, name, unit) for example
    Category for example may be into a merged excel cells so a ffill may be needed first to not lose this info
    The label are concatenated using the joiner_string character.
    '''
    new_columns = frame.columns
    for i in range(start_row, end_row + 1):

        if ffill:  # Treat multi-columns rows
            frame.iloc[i] = frame.iloc[i].fillna(method='ffill')

        if i == start_row:
            new_columns = frame.iloc[i].fillna('')
        else:
            new_columns += joiner_string + frame.iloc[i].fillna('')

    frame.columns = new_columns
    return frame.drop(range(start_row, end_row + 1))


def rename_duplicated_columns(frame, verbose=False):
    '''
    Add a _index suffix for duplicated columns starting at 1
    '''
    dup = get_column_labels_count(frame, True)

    if dup.shape[0] < 1:
        if verbose:
            print("No duplicated columns to rename")
        return frame


    dup_columns_list = list(dup.index)

    dup_columns_counts = dict(zip(dup_columns_list, [0] * len(dup_columns_list)))

    new_columns = list(frame.columns)

    if verbose:
        print("Renaming: ", dup_columns_list)

    for ic, c in enumerate(frame.columns):
        if c in dup_columns_counts:
            new_columns[ic] = c + "_" + str(dup_columns_counts[c] + 1)
            dup_columns_counts[c] += 1

    frame.columns = new_columns

    return frame