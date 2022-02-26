#!/usr/bin/python3
from pydoc import doc, plainpager
import re
import tempfile
from turtle import pos
import nltk
import sys
import getopt
import os
import pickle
import math

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
    # termTracker = {}
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
    
    result.addCorpusDocIDs(sortedDocIDs)
    result.save()
    os.remove(tempFile)


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
                terms.append(stemmer.stem(word.lower()))

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
                pointers = termDict[term][1]

                newPointers = []
                for pointer in pointers:
                    ref.seek(pointer)
                    postings = pickle.load(ref) # loads the array of docIDs

                    postingsWithSP = insertSkipPointers(postings, len(postings))

                    newPointer = output.tell() # new pointer location
                    pickle.dump(postingsWithSP, output) 
                    newPointers.append(newPointer)

                termDictionary.updatePointerList(term, newPointers) 

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
