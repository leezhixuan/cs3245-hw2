#!/usr/bin/python3
from pydoc import doc, plainpager
import re
from turtle import pos
import nltk
import sys
import getopt
import os
import pickle
import math

from TermDictionary import TermDictionary
from SkipList import Node

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below

    tempFile = 'temp.txt'
    limit = 1024
    result = TermDictionary(out_dict)

    tempDict = {}
    # termTracker = {}
    for doc in sorted([int(doc) for doc in os.listdir(in_dir)]):
        terms = generateTermArray(in_dir, doc)

        for term in terms:
            if term not in tempDict.keys():
                # tempDict[term] = [[doc]]
                # termTracker[term] = set()
                # termTracker[term].add(doc)
                tempDict[term] = [set([doc])]
            
            else:
                # if term not in termTracker[term]:
                if (min(len(s) for s in tempDict[term]) < limit):
                    currentSetIndex = len(tempDict[term]) - 1
                    tempDict[term][currentSetIndex].add(doc)

                else:
                    tempDict[term].append(set([doc]))

    # print(tempDict)

    # end of processing all docs
    # format of tempDict = {term : [[doc1, doc2, ..., doc1000], [doc1001, doc1002, ..., doc2000], ...]}
    # no skipPointers yet.

    with open(tempFile, 'wb') as f:
        for term, postingLists in sorted(tempDict.items()):
            for pL in postingLists:
                pointer = f.tell()
                # print(pointer)
                result.addTerm(term, len(pL), pointer)
                # print(term)
                # print(sorted(list(pL)))
                pickle.dump(sorted(list(pL)), f)


    implementSkipPointers(out_postings, tempFile)
    
    # print(retrievePostingsList(tempFile, 54698))



    result.save()


def generateTermArray(dir, doc):
    stemmer = nltk.stem.porter.PorterStemmer()

    terms = []
    with open(os.path.join(dir, str(doc))) as file:
        sentences = nltk.tokenize.sent_tokenize(file.read())
        for sentence in sentences:
            words = nltk.tokenize.word_tokenize(sentence)
            for word in words:
                terms.append(stemmer.stem(word.lower()))

    return terms


def retrievePostingsList(file, pointer):
    with open(file, 'rb') as f:
        f.seek(pointer)
        # print(f.tell())
        return pickle.load(f)

def implementSkipPointers(out_postings, file, termDictionary):
    # with open(file, 'rb') as input:
    #     with open(out_postings, 'wb') as output:

    #         for line in 

    with open(file, 'rb') as ref:
        with open(out_postings, 'rb') as output:

            for term in termDictionary:
                pointers = termDictionary[term][1]

                for pointer in pointers:
                    ref.seek(pointer)
                    postings = pickle.load(ref)

                    postingsWithSP = insertSkipPointers(postings, len(postings))


                    


def insertSkipPointers(postings, length):
    skipInterval = int(math.sqrt(length))
    index = 0

    result = []
    for docID in postings:
        if (index % skipInterval == 0):
            result.append((docID, index + skipInterval))
        
        else:
            result.append((docID, 0))

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
