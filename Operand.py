from cgitb import reset

from numpy import isin


class Operand(object):

    def __init__(self, term=None, result=None):
        self.term = term
        self.isComplemented = False
        self.result = result

    def getTerm(self):
        return self.term

    def complement(self):
        self.isComplemented = True

    def isComplemented(self):
        return self.isComplemented

    def __repr__(self):
        return str(self.term)

    def isTerm(self):
        return not isinstance(self.term, type(None))

    def isResult(self):
        return not isinstance(self.result, type(None))
    
    def getResult(self):
        return self.result
    


    

    