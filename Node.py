from pydoc import doc


class Node(object):

    def __init__(self, docID):
        self.docID = docID
        self.skipPointer = 0 # target index = skipPointer + currentIndex

    def addSkipPointer(self, value):
        self.skipPointer = value

    def hasSkip(self):
        return self.skipPointer != 0
        
    def __str__(self):
        return "(" + str(self.docID) + ", " + str(self.skipPointer) + ")"

    def __repr__(self):
        return "(" + str(self.docID) + ", " + str(self.skipPointer) + ")"

    def getDocID(self):
        return self.docID