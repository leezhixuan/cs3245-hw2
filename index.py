#!/usr/bin/python3
import re
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
import sys
import getopt
import os

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
    limit = 1000
    result = TermDictionary(out_dict)

    tempDict = {}
    for doc in sorted([int(doc) for doc in os.listdir(in_dir)]):
        terms = generateTermArray(in_dir, doc)

        for term in terms:
            if term not in tempDict.keys():
                tempDict[term] = [[doc]]
            
            else:
                if (min(len(arr) for arr in tempDict[term]) < limit):
                    currentArrayIndex = len(tempDict[term]) - 1
                    tempDict[term][currentArrayIndex].append(doc)

                else:
                    tempDict[term].append([doc])

    # end of processing all docs
    # format of tempDict = {term : [[doc1, doc2, ..., doc1000], [doc1001, doc1002, ..., doc2000], ...]}
    # no skipPointers yet.


                        
    








def generateTermArray(dir, doc):
    terms = []
    stemmer = PorterStemmer()

    with open(os.path.join(dir), str(doc)) as f:
        sentences = sent_tokenize(f.read())
        
        for sentence in sentences:
            words = word_tokenize(sentence)
            terms.append([stemmer.stem(word.lower()) for word in words])

    f.close()

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
