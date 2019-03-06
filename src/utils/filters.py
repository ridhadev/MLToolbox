import re



########################################################################################################################

def filter_list(items, filter):
    '''
    Filter a list of items according to a filter
    :param items: Items to filter
    :param filter: Filter to use. Must have a accept() method.
    :return: Filtered list of items
    '''
    return [f for f in items if filter.accept(f)]


########################################################################################################################

class SimpleTextFilter():

    def __init__(self, include_filters = None, exclude_filters = None):
        '''
        :param include_filter: Array of values to exclude
        :param exclude_filter: Array of values to include
        '''
        self.include_filter = include_filters
        self.exclude_filter = exclude_filters

    def accept(self, text):
        if self.exclude_filter:
            if text in self.exclude_filter:
                return False

        if self.include_filter:
            if text not in self.include_filter:
                return False

        return True

    def filter(self, data):
        data_copy = data.copy()
        for d in data :
            if not self.accept(d):
                data_copy.remove(d)

        return data_copy

    def boolean_filter(self, data):
        data_copy = [True] * len(data)
        for id, d in enumerate(data):
            data_copy[id] = self.accept(d)
        return data_copy


    def filter_dict_values(self, dict_data):
        '''
        Filter dictionary values
        :param dict_data:
        :param onkeys:
        :param onvalues:
        :return:
        '''

        data_copy = dict_data.copy()

        for k, v in data_copy.items():
            data_copy[k] = self.filter(data_copy[k])

        return data_copy


########################################################################################################################

class RegexTextFilter(SimpleTextFilter) :

    def __init__(self, include_filters = None, exclude_filters = None):
        '''
        :param include_filter: Regexp of values to exclude
        :param exclude_filter: Regexp of values to include
        '''
        self.include_filter = include_filters
        if self.include_filter :
            self.include_filters = re.compile(include_filters)

        self.exclude_filter = exclude_filters

        if self.exclude_filters:
            self.exclude_filters = re.compile(exclude_filters)

    def accept(self, text):

        if self.exclude_filter and self.exclude_filter.match(text):
            return False

        if self.include_filter and not self.include_filter.match(text):
            return False

        return True

########################################################################################################################