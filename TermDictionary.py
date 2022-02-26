import pickle

class TermDictionary(object):

    DOCFREQ_INDEX = 0
    POINTERS_INDEX = 1

    def __init__(self, storageLocation):
        self.termInformation = {} # In the form of {term: [docFrequency, [pointer1, pointer2, pointer3, ...]]}
        self.storageLocation = storageLocation

    def addTerm(self, term, docFrequency, pointer):
        if term in self.termInformation.keys():
            self.termInformation[term][self.DOCFREQ_INDEX] += docFrequency
            self.termInformation[term][self.POINTERS_INDEX].append(pointer)
        
        else:
            self.termInformation[term] = [docFrequency, [pointer]]
    
    def getTermPointers(self, term):
        try:
            termPointers = self.termInformation[term][self.POINTERS_INDEX]
            return termPointers
        except KeyError:
            return []
    
    def save(self):
        with open(self.storageLocation, 'wb') as f:
            pickle.dump(self.termInformation, f)
        f.close()

    def load(self):
        with open(self.storageLocation, 'rb') as f:
            self.termInformation = pickle.load(f)
        f.close()

    def updatePointerList(self, term, newPointerList):
        self.termInformation[term][self.POINTERS_INDEX] = newPointerList

    def getTermDict(self):
        return self.termInformation

    def getTermDocFrequency(self, term):
        try:
            docFrequency = self.termInformation[term][self.DOCFREQ_INDEX]
            return docFrequency
        except KeyError:
            return 0

    def addCorpusDocIDs(self, allDocIDs):
        self.termInformation["c0rpu5D1r3ct0ry"] = allDocIDs

    def getCorpusDocIDs(self):
        return self.termInformation["c0rpu5D1r3ct0ry"]
    