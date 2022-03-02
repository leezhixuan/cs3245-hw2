import pickle
import os
import math

from TermDictionary import TermDictionary

def SPIMIInvert(tokenStream, outputFile, dictFile):
    """
    This function is akin to the one we've seen the in textbook. Each call to
    SPIMIInvert writes a block to disk.
    """
    tempDict = {} # {term : set(docIDs)}
    termDict = TermDictionary(dictFile)

    for termDocIDPair in tokenStream: # tokenStream is in the form of [(term1, docID), (term2, docID), ...]
        term = termDocIDPair[0]
        docID = termDocIDPair[1]
        if termDocIDPair[0] not in tempDict:
            tempDict[term] = set([docID])
        else:
            tempDict[term].add(docID) # duplicate docIDs will not be added into Sets
    

    with open(outputFile, 'wb') as f:
        for term in sorted(tempDict): # {term : set(docIDs)}
            pointer = f.tell()
            pickle.dump(list(tempDict[term]), f) # store list of docIDs into outputFile
            termDict.addTerm(term, len(tempDict[term]), pointer) # update TermDictionary
    
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

def mergeDictsAndPostings(dictFile1, postingsFile1, dictFile2, postingsFile2, outputdictFile, outputPostingsFile):
    """
    This function serves to merge 2 dictionaries and their respective postings files into 1 dictionary and 1 postings file.
    """
    termDict = TermDictionary(outputdictFile) # output dictionary after merging
    dict1 = TermDictionary(dictFile1)
    dict1.load()
    dict2 = TermDictionary(dictFile2)
    dict2.load()
    
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
        unionOfKeys = sorted(keySet1.union(keySet2)) # all (unique) keys from the 2 dictionaries to be merged.

        for key in unionOfKeys:
            postings1 = set(retrievePostingsList(postingsFile1, dict1.getTermPointer(key))) #retrieves postingsList if term is present, else []
            postings2 = set(retrievePostingsList(postingsFile2, dict2.getTermPointer(key)))
            sortedMergePostings = sorted(postings1.union(postings2)) #merging then sorting docIDs
            pointer = output.tell()
            termDict.addTerm(key, len(sortedMergePostings), pointer)
            pickle.dump(sortedMergePostings, output)

    # end of merging dictionaries and postings file
    # delete the files that have been merged to free up space.
    os.remove(dictFile1)
    os.remove(dictFile2)
    os.remove(postingsFile1)
    os.remove(postingsFile2)
    termDict.save()


def binaryMerge(dir, fileIDs, outputPostingsFile, outputDictFile):
    """
    Performs binary merge on all files in the specified directory.
    """
    for stage in range(math.ceil(math.log2(fileIDs))): # no. of times we merge is proportional to the no. of unique fileIDs in the directory
        newFileID = 0 # to merged file identifier
        for ID in range(0, fileIDs, 2): # merge files_docID with files_ID+1
            if ID + 1 < fileIDs:
                dictFile1 = dir + 'tempDictionaryFile' + str(ID) + '_stage' + str(stage) + '.txt'
                dictFile2 = dir + 'tempDictionaryFile' + str(ID + 1) + '_stage' + str(stage) + '.txt'
                postingsFile1 = dir + 'tempPostingFile' + str(ID) + '_stage' + str(stage) + '.txt'
                postingsFile2 = dir + 'tempPostingFile' + str(ID + 1) + '_stage' + str(stage) + '.txt'
                outDictFile = dir + 'tempDictionaryFile' + str(newFileID) + '_stage' + str(stage + 1) + '.txt'
                outPostingsFile = dir + 'tempPostingFile' + str(newFileID) + '_stage' + str(stage + 1) + '.txt'
                mergeDictsAndPostings(dictFile1, postingsFile1, dictFile2, postingsFile2, outDictFile, outPostingsFile)
                
            else: # there is an odd number of files in the directory
                oldDictFile = dir + 'tempDictionaryFile' + str(ID) + '_stage' + str(stage) + '.txt'
                newDictFile = dir + 'tempDictionaryFile' + str(newFileID) + '_stage' + str(stage + 1) + '.txt'
                oldPostingsFile = dir + 'tempPostingFile' + str(ID) + '_stage' + str(stage) + '.txt'
                newPostingsFile = dir + 'tempPostingFile' + str(newFileID) + '_stage' + str(stage + 1) + '.txt'
                os.rename(oldDictFile, newDictFile)
                os.rename(oldPostingsFile, newPostingsFile)
            
            newFileID+=1
        fileIDs = newFileID

    # here, i will only have 1 dictionary.txt and 1 postings.txt (the end)
    # move these out into the main directory.
    IDOfLeftoverFiles = newFileID - 1
    StageOfLeftoverFiles = stage + 1
    os.rename(dir + 'tempDictionaryFile' + str(IDOfLeftoverFiles) + '_stage' + str(StageOfLeftoverFiles) + '.txt', outputDictFile)
    os.rename(dir + 'tempPostingFile' + str(IDOfLeftoverFiles) + '_stage' + str(StageOfLeftoverFiles) + '.txt', outputPostingsFile)




