

####################### Dict ##################################################

def reverse_dict(adict, new_values_type='array'):
    '''
    Reverse a dictionnary key: values -> value: key
    :param adict: the dictionnary to reverse
    :param new_values_type: If 'array' the new dictionnary is mapped against values as array; a single entry otherwise
    :return: Reversed map
    '''

    inv_map = {}

    for k, v in adict.items():
        if new_values_type == 'array':
            inv_map[v] = inv_map.get(v, [])
            inv_map[v].append(k)
        else :
            inv_map[v] = k

    return inv_map


