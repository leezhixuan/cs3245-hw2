class QueryTerm(object):

    def __init__(self, term):
        self.term = term
        self.isComplemented = False

    def getTerm(self):
        return self.term

    def complement(self):
        self.isComplemented = True

    def isComplemented(self):
        return self.isComplemented

    def __repr__(self):
        return str(self.term)
