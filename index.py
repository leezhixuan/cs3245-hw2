#!/usr/bin/python3
from pydoc import plainpager
import re
from turtle import pos
import nltk
import sys
import getopt
import os
import pickle

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
                result.addTerm(term, len(pL), pointer)
                print(term)
                print(sorted(list(pL)))
                pickle.dump(pL, f)

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
