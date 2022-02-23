#!/usr/bin/python3
from ast import operator
import re
import nltk
import sys
import getopt
import pickle

from TermDictionary import TermDictionary

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below

    termDict = TermDictionary(dict_file)
    termDict.load()

def splitQuery(query):
    """
    Takes in a query string and splits it into an array of query terms and operators,
    without spaces
    """
    temp = nltk.tokenize.word_tokenize(query)
    stemmer = nltk.stem.porter.PorterStemmer()
    result = []
    for term in temp:
        if not isOperator(term):
            result.append(stemmer.stem(term.lower()))
        else:
            result.append(term)
    
    # # removes the need to process NOT, then AND separately.
    # for i in range(len(result) - 1):
    #     if result[i] == "AND" and result[i+1] == "NOT":
    #         result[i] = "ANDNOT"
    #     elif result[i] == "OR" and result[i+1] == "NOT":
    #         result[i] = "ORNOT"

    # result = list(filter(lambda term: term != "NOT", result))
    return result
        
    
def shuntingYard(query):
    operatorStack = [] #enters from the back, exits from the back
    output = []

    queryTerms = splitQuery(query)
    for term in queryTerms:

        if term == '(':
            operatorStack.append(term)

        elif term == ')':
            while (len(operatorStack) > 0 and operatorStack[len(operatorStack) - 1] != "("):
                output.append(operatorStack.pop())

            operatorStack.pop() # discards "("
        elif isOperator(term):
            while (len(operatorStack) > 0 and operatorStack[len(operatorStack) - 1] != "(" and isOfGreaterPrecedence(operatorStack[len(operatorStack) - 1], term)):
                output.append(operatorStack.pop())

            operatorStack.append(term)

        else:
            output.append(term)

    for operator in operatorStack:
        output.append(operator)
          
    return output


def evaluateRPN(RPNexpression):
    """
    evaluates the input expression (in reverse polish expression) and returns an array of docIDs found
    """
    processStack = [] #enters from the back, exits from the back

    for element in RPNexpression:
        if not isOperator(element):
            postingsLists = []
            
        
        else:
            # element is an operator
            if element == "NOT":
                operand = ""

        
def isOfGreaterPrecedence(operator1, operator2):
    operatorPrecedence = {"NOT": 3, "AND": 2, "OR" : 1}
    # operatorPrecedence =  {"ANDNOT": 5, "ORNOT": 4, "NOT": 3, "AND": 2, "OR" : 1}
    # {"(": 4, ")" : 4, "NOT" : 3, "AND": 2, "OR" : 1}
    return operatorPrecedence[operator1] > operatorPrecedence[operator2]

def isOperator(term):
    operators = ["(", ")", "NOT", "AND", "OR"]
    return term in operators
    
def retrievePostingsList(file, pointer):
    with open(file, 'rb') as f:
        f.seek(pointer)
        # print(f.tell())
        # reurn pickle.load(f)
        postingsList = pickle.load(f)
    f.close()

    return postingsList

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
