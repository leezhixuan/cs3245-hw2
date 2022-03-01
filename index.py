#!/usr/bin/python3
import shutil
import nltk
import sys
import getopt
import os
import pickle
import math

from AuxiliaryDictionary import AuxiliaryDictionary
from TermDictionary import TermDictionary
from Node import Node

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    tempFile = 'temp.txt'
    limit = 1024 # max number of terms in each postings list
    result = TermDictionary(out_dict)

    sortedDocIDs = sorted([int(doc) for doc in os.listdir(in_dir)])
    tempDict = {}
    for doc in sortedDocIDs:
        terms = generateTermArray(in_dir, doc) # returns an array of terms present in that particular doc

        for term in terms:
            # each term has an array of sets. Each set contains at most 1024 unique docID
            if term not in tempDict.keys():
                tempDict[term] = [set([doc])] 
            
            else:
                # if term not in termTracker[term]:
                if (min(len(s) for s in tempDict[term]) < limit):
                    currentSetIndex = len(tempDict[term]) - 1
                    tempDict[term][currentSetIndex].add(doc)

                else:
                    # all preceding sets are full, hence the need for a new set.
                    tempDict[term].append(set([doc]))

    # end of processing all docs
    with open(tempFile, 'wb') as f:
        for term, postingLists in sorted(tempDict.items()):
            for pL in postingLists:
                pointer = f.tell() # current location in disk
                result.addTerm(term, len(pL), pointer) # create/update entry in resultant dictionary (i.e dictionary.txt)
                pickle.dump(sorted(list(pL)), f) # save current postings list onto disk, into temp.txt
    f.close()

    implementSkipPointers(out_postings, tempFile, result) # add skip pointers to posting list and save them to postings.txt
    
    # result.addCorpusDocIDs(sortedDocIDs) #add all docIDs in the corpus to the dictionary

    with open(out_postings, 'ab') as f:
        pointer = f.tell()
        print(pointer)
        result.addPointerToCorpusDocIDs(pointer)
        pickle.dump([Node(n) for n in sortedDocIDs], f)
    f.close()

    result.save()
    os.remove(tempFile)

# def build_index(in_dir, out_dict, out_postings):
#     """
#     build index from documents stored in the input directory,
#     then output the dictionary file and postings file
#     """
#     print('indexing...')

#     tempFile = 'temp.txt'
#     tempDictFile = 'tempDict.txt'
#     tempPostingsDirectory = "tempPostingsDirectory/"
#     limit = 512 # max number of files in each block
#     auxDict = AuxiliaryDictionary(tempDictFile)
#     result = TermDictionary(out_dict)

#     if not os.path.exists(tempPostingsDirectory):
#         os.mkdir(tempPostingsDirectory)
#     else:
#         shutil.rmtree(tempPostingsDirectory) #delete the specified directory tree for re-indexing purposes
#         os.mkdir(tempPostingsDirectory)

#     sortedDocIDs = sorted([int(doc) for doc in os.listdir(in_dir)])

#     for doc in sortedDocIDs:
#         terms = generateTermArray(in_dir, doc) # returns an array of terms present in that particular doc

#         for term in terms:
#             if limit > count:
#                 # each term has an array of sets. Each set contains at most 1024 unique docID
#                 if term not in tempDict:
#                     tempDict[term] = [1, set(doc)]
#                     count+=1
                
#                 else: # term and docID already in tempDict
#                     if doc in tempDict[term][1]:
#                         count+=1

#                     else: # it is the same term, but different docID
#                         tempDict[term][0] += 1
#                         tempDict[term][1].add(doc)
#                         count+=1
#             else:
#                 auxDict.load() 
#                 auxDict.mergeDict(tempDict)
#                 tempDict = {}
#                 auxDict.save()
        
#     # end of processing all docs
#     sortedTerms = sorted(auxDict.getDict().keys())
#     with open(tempFile, 'wb') as f:
#         for term in sortedTerms:
#             docIDs = term
#             pointer = f.tell() # current location in disk
#             result.addTerm(term, len(), pointer) # create/update entry in resultant dictionary (i.e dictionary.txt)
#             pickle.dump(sorted(list(pL)), f) # save current postings list onto disk, into temp.txt
    
#     f.close()

#     implementSkipPointers(out_postings, tempFile, result) # add skip pointers to posting list and save them to postings.txt
    
#     result.addCorpusDocIDs(sortedDocIDs) #add all docIDs in the corpus to the dictionary
#     result.save()
#     os.remove(tempFile)


# def SPIMIInvert(tokenStream, docID, tempFile):
#     tempDict = {}
#     memory = 2048
#     count = 0
#     for token in tokenStream:
#         if memory > 0:
#             if token not in tempDict:
#                 tempDict[token] = docID
            

        


def generateTermArray(dir, doc):
    """
    Given a document and the directory, we stem all terms present in 
    the document by stemming them, then output the stemmed terms as an array
    """
    stemmer = nltk.stem.porter.PorterStemmer()

    terms = []
    with open(os.path.join(dir, str(doc))) as file:
        sentences = nltk.tokenize.sent_tokenize(file.read())
        for sentence in sentences:
            words = nltk.tokenize.word_tokenize(sentence)
            for word in words:
                terms.append(stemmer.stem(word.lower())) # stemming + case-folding

    return terms


def implementSkipPointers(out_postings, file, termDictionary):
    """
    Add skip pointers to the postings lists present in file, update pointers in termDictionary and
    save the new postings lists (with skip pointers) into out_postings
    """
    with open(file, 'rb') as ref:
        with open(out_postings, 'wb') as output:

            termDict = termDictionary.getTermDict()
            for term in termDict:
                pointers = termDict[term][1] #retrieves the list of pointers associated to the term

                docIDs = []
                for pointer in pointers:
                    ref.seek(pointer)
                    postings = pickle.load(ref) # loads the array of docIDs

                    docIDs.extend(postings) # merge postings

                postingsWithSP = insertSkipPointers(sorted(set(docIDs)), len(docIDs)) # insert skip pointers
                newPointer = output.tell() # new pointer location
                pickle.dump(postingsWithSP, output)
                termDictionary.updatePointerToPostings(term, newPointer) # term entry is now --> term : [docFreq, pointer]

        output.close()
    ref.close()


def insertSkipPointers(postings, length):
    """
    Given an array of postings, transform each docID into a Node. Add skip pointers
    at regular skip intervals and output an array of Nodes.
    """
    skipInterval = int(math.sqrt(length))
    endOfIndex = length - 1
    currentIndex = 0

    result = []
    for docID in postings:
        node = Node(docID)
        if (currentIndex % skipInterval == 0 and currentIndex + skipInterval <= endOfIndex):
            # makes sure that it is time for a skip pointer to be inserted and it is not inserted into
            # a node that will facilitate a skip past the last node.
            node.addSkipPointer(skipInterval)
            result.append(node)
        
        else:
            result.append(node)

        currentIndex+=1

    return result

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
