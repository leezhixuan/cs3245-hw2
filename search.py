#!/usr/bin/python3
from ast import operator
import re
import nltk
import sys
import getopt
import pickle

from TermDictionary import TermDictionary
from Operand import Operand

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
    ['NOT', '(', 'a', 'OR', 'b', ')', 'AND', '(', 'NOT', 'c', 'OR', 'NOT', 'd', ')', 'AND', '(', 'e', 'OR', 'f', ')' ]
    ['a', 'b', 'OR', 'NOT', 'c', 'NOT', 'd', 'NOT', 'OR', 'e', 'f', 'OR', 'AND', 'AND']
    """
    Takes in a query string and splits it into an array of query terms and operators,
    without spaces
    """
    # possible idea: convert query terms into QueryTerm objects here. Eliminate the presence of NOT operators in the resultant output by
    # representing it in the isComplemented attribute of the QueryTerm. This removes the need for a NOT method as well.
    temp = nltk.tokenize.word_tokenize(query)
    stemmer = nltk.stem.porter.PorterStemmer()
    result = []
    for term in temp:
        if not isOperator(term):
            result.append(stemmer.stem(term.lower()))
        else:
            result.append(term)
    # # scraped because it doesnt account for the first term having NOT
    # # # removes the need to process NOT, then AND separately.
    # # for i in range(len(result) - 1):
    # #     if result[i] == "AND" and result[i+1] == "NOT":
    # #         result[i] = "ANDNOT"
    # #     elif result[i] == "OR" and result[i+1] == "NOT":
    # #         result[i] = "ORNOT"
    # output = []
    # for i in range(len(result) - 1):
    #     if result[i] == "NOT" and not isOperator(result[i+1]): # complemented term
    #         qTerm = QueryTerm(result[i])
    #         qTerm.complement()
    #         output.append(qTerm)
    #     elif isOperator(result[i]):
    #         output.append(result[i])
    #     else: #normal term
    #         qTerm = QueryTerm(result[i])
    #         output.append(qTerm)     
    # output = list(filter(lambda qTerm: qTerm != "NOT", output))
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
        output.append(operatorStack.pop())
    return output


def evaluateRPN(RPNexpression, dict_file, postings_file):
    "[X, 'c', 'd', ...]"
    """
    evaluates the input expression (in reverse polish expression) and returns an array of docIDs found
    """
    processStack = [] #enters from the back, exits from the back

    for element in RPNexpression:
        if not isOperator(element):
            # postingsLists = []
            processStack.append(element)
            
        else:
            # element is an operator
            if element == "NOT": #create a new class QueryTerm that stores isComplemented
                firstOperand = processStack.pop() # term to be complemented
                pass

        
def isOfGreaterPrecedence(operator1, operator2):
    operatorPrecedence = {"NOT": 3, "AND": 2, "OR" : 1}
    # operatorPrecedence =  {"ANDNOT": 5, "ORNOT": 4, "NOT": 3, "AND": 2, "OR" : 1}
    # {"(": 4, ")" : 4, "NOT" : 3, "AND": 2, "OR" : 1}
    return operatorPrecedence[operator1] > operatorPrecedence[operator2]

def isOperator(term):
    operators = ["(", ")", "NOT", "AND", "OR"]
    return term in operators

# def retrievePostingsLists(termDict, postings_file, term):
#     pointers = termDict.getTermPointers()
#     postingsLists = 
#     with open(postings_file, 'rb') as f:
#         for
#         f.seek(pointer)
#         # print(f.tell())
#         # reurn pickle.load(f)
#         postingsList = pickle.load(f)
#     f.close()
    
def retrievePostingsList(file, pointer):
    with open(file, 'rb') as f:
        f.seek(pointer)
        # print(f.tell())
        # reurn pickle.load(f)
        postingsList = pickle.load(f)
    f.close()

    return postingsList

def AND(queryTerm1, queryTerm2):
    pass

def OR(queryTerm1, queryTerm2):
    'c', 'NOT', 'd', 'NOT', 'OR'
    if queryTerm1.isComplemented():
        #produce an array of docIDs that doesnt contain term1
        pass

    if queryTerm2.isComplemented():
        pass

def NOT(queryTerm):
    pass


def mergeAND(postingList1, postingList2):
    pass

def mergeOR(postingList1, postingList2):
    pass

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
