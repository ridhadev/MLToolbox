from data.frames import *


class FrameDescriptor :
    def __init__(self, frame):
        self.__df__ = frame.copy()
        self.__dirty__ = True


    @property
    def df(self):
        return self.__df__.copy()

    def update_descriptor(self):
        self.__desc__ = get_columns_desc(self.__df__)
        self.__dirty__ = False

    def get_columns_descriptor(self):

        if self.__dirty__ :
            self.__do_update_descriptor__()

        return self.__desc__

    def get_size_info(self):
        pass

    def get_column_names(self):
        pass

    def get_empty_columns_or_rows(self, columns=True):
        pass

    def get_misfilled_columns_or_rows(self, columns=True, threshold=0.5):
        pass

    def compare_to(self, descriptor, attribute='%fill'):
        pass