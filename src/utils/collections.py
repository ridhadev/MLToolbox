

####################### Dict ##################################################
def reverse_dict(adict):
    '''
    Reverse a dictionnary
    :param adict: the dictionnry to reverse
    :return:
    '''
    inv_map = {}
    for k, v in adict.items():
        inv_map[v] = inv_map.get(v, [])
        inv_map[v].append(k)
    return inv_map