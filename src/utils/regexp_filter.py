import re

class RegexpFilter():
    def __init__(self, include_regexp= None, exclude_regexp = None):
        if include_regexp :
            self.include_regexp = re.compile(include_regexp)
        else:
            self.include_regexp = None

        if exclude_regexp :
            self.exclude_regexp = re.compile(exclude_regexp)
        else:
            self.exclude_regexp = None

    #
    def select(self, expression):
        '''
        
        :param expression:
        :return:
        '''
        if self.exclude_regexp and self.exclude_regexp.match(expr):
           return False

        if self.include_regexp and (not self.include_regexp.match(expr)):
            return False

        return True

    def filter(self, expressions):
         return [expr for expr in filtered if self.select(expr)]
