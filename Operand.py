from cgitb import reset


class Operand(object):

    def __init__(self, term=None, result=[]):
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
        return len(self.result) == 0

    def isResult(self):
        return len(self.result) > 0
    
    def getResult(self):
        return self.result
    


    

    