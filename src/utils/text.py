'''
    Utility methods to query and edit text string
'''

import re


########################### Edit ####################################################

##########################
###### Remove ############
##########################

def remove_repetitive_chars(astring, achar = ' '):
    '''
    Removes repetitive chars by only one occurence of that one
    '''
    return re.sub(achar + '+', achar, astring)


def remove_special_chars(astring, filter_lambda=lambda x: (x.isalnum() or x == ' ')):
    '''
    :param astring:
    :param filter_lambda:
    :return: Remove all non alpha-numeric or space characters
    '''
    return ''.join(e for e in astring if filter_lambda(e))



###### Replace ######
def replace_superscript_digits(astring):
    '''
    Replaces superscript numric digit by "normal" ones
    :param astring:
    :return:
    '''
    return replace_special_chars(astring, dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")))


def replace_special_chars(astring, char_map):
    '''
    Replaces a set of characters by another using a provided map
    :param astring:
    :param char_map:
    :return: Edited text
    .. seealso:: replace_superscript_digits()
    '''
    for k, v in char_map.items():
        if k in astring:
            astring = astring.replace(k, v)
    return astring



