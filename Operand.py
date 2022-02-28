class Operand(object):
    """
    Operand is a class that encapsulates the attributes and behaviour of an operand in logical expressions.
    It serves to simplify the evaluation of logical expressions.
    """

    def __init__(self, term=None, result=None):
        self.term = term
        self.result = result
        # self.docFreq = docFreq


    def __repr__(self):
        return str(self.term)

    # def __eq__(self, other):
    #     return self.docFreq == other.docFreq

    # def __ne__(self, other):
    #     return self.docFreq != other.docFreq

    # def __lt__(self, other):
    #     return self.docFreq < other.docFreq

    # def __le__(self, other):
    #     return self.docFreq <= other.docFreq

    # def __gt__(self, other):
    #     return self.docFreq > other.docFreq

    # def __ge__(self, other):
    #     return self.docFreq >= other.docFreq


    def isTerm(self):
        """
        Checks if Operand is a term and not a result
        """
        return not isinstance(self.term, type(None))


    def isResult(self):
        """
        Checks if Operand is a result and not a term 
        """
        return not isinstance(self.result, type(None))
    

    def getResult(self):
        return self.result

    
    def getTerm(self):
        return self.term
    