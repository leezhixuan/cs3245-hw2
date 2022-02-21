class Node(object):

    def __init__(self, docID):
        self.docID = docID
        self.skipTo = None
        self.next = None

    def hasSkip(self):
        if isinstance(self.skipTo, None):
            return False

        return True
    
    def skip(self):
        return self.skipTo

    def getDocID(self):
        return self.docID

    def hasNextNode(self):
        if isinstance(self.next, None):
            return False
        
        return True

    def addNextNode(self, nextNode):
        self.next = nextNode

        
