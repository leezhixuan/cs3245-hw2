import pickle
import os
import math

from TermDictionary import TermDictionary

def SPIMIInvert(tokenStream, outputFile, dictFile):
    tempDict = {}
    termDict = TermDictionary(dictFile)
    for termDocIDPair in tokenStream:
        term = termDocIDPair[0]
        docID = termDocIDPair[1]
        if termDocIDPair[0] not in tempDict:
            tempDict[term] = set([docID])
        else:
            tempDict[term].add(docID)
    

    with open(outputFile, 'wb') as f:
        for term in sorted(tempDict): # {term : set(docIDs)}
            pointer = f.tell()
            pickle.dump(list(tempDict[term]), f)
            termDict.addTerm(term, len(tempDict[term]), pointer)
    
    termDict.save()

def retrievePostingsList(file, pointer):
    """
    Given a pointer to determine the location in disk, 
    retrieves the postings list from that location.
    """
    if pointer == -1: # for non-existent terms
        return []

    with open(file, 'rb') as f:
        f.seek(pointer)
        postingsList = pickle.load(f)

    return postingsList

# def merge(set1, set2):
#     return set1.union(set2)

def mergeDictsAndPostings(dictFile1, postingsFile1, dictFile2, postingsFile2, outputdictFile, outputPostingsFile):
    termDict = TermDictionary(outputdictFile) # output dictionary after merging
    dict1 = TermDictionary(dictFile1)
    dict1.load()
    # dict1Dictionary = dict1.getTermDict() # {term: [docFreq, pointer]}
    dict2 = TermDictionary(dictFile2)
    dict2.load()
    # dict2Dictionary = dict2.getTermDict() # {term: [docFreq, pointer]}
    # with open(dictFile1, 'rb') as inputDict1, open(dictFile2, 'rb') as inputDict2, open(postingsFile1, 'rb') as inPostings1, open(postingsFile2, 'rb') as inPostings2:
    
    # what I want is to merge 2 dictionaries
    # use term pointers in them to access the postingIDs
    # create a new TermDictionary
    # retrieve the 2 sets of postingsIDs, combine them together
    # get pointer in outputposting file, f.tell()
    # dump the combined postings list into this file
    # update TermDictionary with the term, docFreq (size of set), and pointer
    with open(outputPostingsFile, 'wb') as output:
        keySet1 = set(dict1.getAllKeys())
        keySet2 = set(dict2.getAllKeys())
        unionOfKeys = keySet1.union(keySet2) # if key present, return relevant info. Else, docFreq = 0, pointer = -1

        for key in unionOfKeys:
            postings1 = set(retrievePostingsList(postingsFile1, dict1.getTermPointer(key)))
            postings2 = set(retrievePostingsList(postingsFile2, dict2.getTermPointer(key)))
            sortedMergePostings = sorted(postings1.union(postings2)) #merging then sorting docIDs
            pointer = output.tell()
            termDict.addTerm(key, len(sortedMergePostings), pointer)
            pickle.dump(sortedMergePostings, output)

    #end all merging dictionaries and postings file
    os.remove(dictFile1)
    os.remove(dictFile2)
    os.remove(postingsFile1)
    os.remove(postingsFile2)
    termDict.save()


def binaryMerge(dir, fileIDs, outputPostingsFile, outputDictFile):
    noOfFiles =  len(os.listdir(dir))

    for stage in range(math.ceil(math.log2(noOfFiles))): # no. of times we merge is proportional to the no. of files in the directory
        newFileID = 0
        for ID in range(0, fileIDs, 2): # merge files_docID with files_ID+1
            if ID + 1 < fileIDs:
                dictFile1 = dir + 'tempDictionaryFile' + str(ID) + '_stage' + str(stage) + '.txt'
                dictFile2 = dir + 'tempDictionaryFile' + str(ID + 1) + '_stage' + str(stage) + '.txt'
                postingsFile1 = dir + 'tempPostingFile' + str(ID) + '_stage' + str(stage) + '.txt'
                postingsFile2 = dir + 'tempPostingFile' + str(ID + 1) + '_stage' + str(stage) + '.txt'
                outDictFile = dir + 'tempDictionaryFile' + str(newFileID) + '_stage' + str(stage + 1) + '.txt'
                outPostingsFile = dir + 'tempPostingFile' + str(newFileID) + '_stage' + str(stage + 1) + '.txt'
                mergeDictsAndPostings(dictFile1, postingsFile1, dictFile2, postingsFile2, outDictFile, outPostingsFile)
                newFileID+=1

            else: # there is an odd number of files in the directory
                oldDictFile = dir + 'tempDictionaryFile' + str(ID) + '_stage' + str(stage) + '.txt'
                newDictFile = dir + 'tempDictionaryFile' + str(newFileID) + '_stage' + str(stage + 1) + '.txt'
                oldPostingsFile = dir + 'tempPostingFile' + str(ID) + '_stage' + str(stage) + '.txt'
                newPostingsFile = dir + 'tempPostingFile' + str(newFileID) + '_stage' + str(stage + 1) + '.txt'
                os.rename(oldDictFile, newDictFile)
                os.rename(oldPostingsFile, newPostingsFile)
        
        fileIDs = newFileID
        newFileID = 0

    # here, i will only have 1 dictionary.txt and 1 postings.txt, but what are they named?
    os.rename(dir + 'tempDictionaryFile' + str(newFileID) + '_stage' + str(stage + 1) + '.txt', outDictFile)
    os.rename(dir + 'tempPostingFile' + str(newFileID) + '_stage' + str(stage + 1) + '.txt', outputPostingsFile)




