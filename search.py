#!/usr/bin/python3
from concurrent.futures import process
import nltk
import sys
import getopt
import pickle

from TermDictionary import TermDictionary
from Operand import Operand
from Node import Node


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    termDict = TermDictionary(dict_file)
    termDict.load() # load term information into termDict from dict_file

    with open(queries_file, 'r') as queryFile:
        with open(results_file, 'w') as resultFile:
            allResult = []

            for query in queryFile:
                if query.strip(): # if query is not blank after removing spaces from both ends
                    RPNExpression = shuntingYard(query)
                    result = evaluateRPN(RPNExpression, termDict, postings_file)
                    allResult.append(result)
                else:
                    allResult.append("") # blank queries

            outputResult = "\n".join(allResult) # to output all result onto a new line.
            resultFile.write(outputResult)

        resultFile.close()
    queryFile.close()


def splitQuery(query):
    """
    Takes in a query string and splits it into an array of query terms and operators,
    without spaces
    """
    temp = nltk.tokenize.word_tokenize(query)
    stemmer = nltk.stem.porter.PorterStemmer() # stem query like how we stem terms in corpus
    result = []
    for term in temp:
        if not isOperator(term): # don't case-fold operators
            result.append(stemmer.stem(term.lower()))
        else: # term is an Operator
            result.append(term)
    return result


def shuntingYard(query):
    """
    This is the Shunting-yard algorithm. It parses a query string and returns them
    in Reverse Polish Notation.
    """
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
    while(len(operatorStack) > 0): 
        output.append(operatorStack.pop())
    return output


def evaluateRPN(RPNexpression, dict_file, postings_file):
    """
    evaluates the input expression (in reverse polish expression) and returns an array of docIDs found
    """
    processStack = [] #enters from the back, exits from the back

    if "OR" not in RPNexpression and "NOT" not in RPNexpression:
        processStack = optimisedEvalAND(processStack, RPNexpression, dict_file, postings_file)

    else: 
        for qTerm in RPNexpression:
            if isOperator(qTerm):
                if qTerm == "NOT": # unary operator
                    operand1 = processStack.pop()
                    processStack.append(evalNOT(operand1, dict_file, postings_file))
                elif qTerm == "AND": # binary operator
                    operand1 = processStack.pop()
                    operand2 = processStack.pop()
                    processStack.append(evalAND(operand1, operand2, dict_file, postings_file))
                else: # qTerm is "OR", a binary operator
                    operand1 = processStack.pop()
                    operand2 = processStack.pop()
                    processStack.append(evalOR(operand1, operand2, dict_file, postings_file))
            else: # qTerm is not an operator
                operand = Operand(qTerm, result=None)
                processStack.append(operand)
    
    # at the end, the processStack will contain just 1 Operand, which could be an array of 
    # result already (in the case where the query is a combination e.g. "hi AND bye"), 
    # or simply just a term (in the case where the query is only 1 word e.g. "hello")

    termOrResult = processStack[0] # covers the case where the query is a single term (e.g. "hi")
    if termOrResult.isTerm():
        processStack.append(evalTerm(processStack.pop(), dict_file, postings_file))

    return " ".join([str(docID) for docID in processStack.pop().getResult()])


def optimisedEvalAND(processStack, RPNExpression, dict_file, postings_file):
    # RPN is a purely conjunctive query
    # processStack = sorted([Operand(term=t, result=None, docFreq=dict_file.getTermDocFrequency(t)) for t in list(filter(lambda a: a!= "AND", RPNExpression))])
    processStack = [Operand(term=t, result=None) for t in sorted(list(filter(lambda a: a!= "AND", RPNExpression)), key=dict_file.getTermDocFrequency, reverse=True)]
    
    while len(processStack > 1):
        operand1 = processStack.pop()
        operand2 = processStack.pop()
        processStack.append(evalAND(operand1, operand2, dict_file, postings_file))
    
    return processStack

    
def isOfGreaterPrecedence(operator1, operator2):
    """
    Given 2 operators, operator1 and operator2, determine if operator1 is
    of greater precedence than operator2.
    """
    operatorPrecedence = {"NOT": 3, "AND": 2, "OR" : 1}
    return operatorPrecedence[operator1] > operatorPrecedence[operator2]


def isOperator(term):
    """
    Checks if the given term is an operator.
    """
    operators = ["NOT", "AND", "OR"]
    return term in operators


def retrievePostingsList(file, pointer):
    """
    Given a pointer to determine the location in disk, 
    retrieves the postings list from that location.
    """
    with open(file, 'rb') as f:
        f.seek(pointer)
        postingsList = pickle.load(f)
    f.close()

    return postingsList


def evalAND(operand1, operand2, dictFile, postingsFile):
    """
    input: TermDictionary as dictFile
    input: name of posting file as postingsFile
    output: Operand containing result
    Calls evalAND_terms/evalAND_term_result/evalAND_results depending on operand types
    """
    # Both inputs are terms
    if operand1.isTerm() and operand2.isTerm():
        term1, term2 = operand1.getTerm(), operand2.getTerm()
        result = evalAND_terms(term1, term2, dictFile, postingsFile)

    # Input 1 is term, Input 2 is result
    elif operand1.isTerm() and operand2.isResult():
        term = operand1.getTerm()
        res = operand2.getResult()
        result = evalAND_term_result(term, res, dictFile, postingsFile)

    # Input 2 is term, Input 1 is result
    elif operand2.isTerm() and operand1.isResult():
        term = operand2.getTerm()
        res = operand1.getResult()
        result = evalAND_term_result(term, res, dictFile, postingsFile)

    # Both inputs are results
    else:
        result1 = operand1.getResult()
        result2 = operand2.getResult()
        result = evalAND_results(result1, result2)

    return Operand(term=None, result=result)


def evalOR(operand1, operand2, dictFile, postingsFile):
    """
    input: TermDictionary as dictFile
    input: name of posting file as postingsFile
    output: Operand containing result
    Calls evalOR_terms/evalOR_term_result/evalOR_results depending on operand types
    """
    # Both inputs are terms
    if operand1.isTerm() and operand2.isTerm():
        term1, term2 = operand1.getTerm(), operand2.getTerm()
        result = evalOR_terms(term1, term2, dictFile, postingsFile)

    # Input 1 is term, Input 2 is result
    elif operand1.isTerm() and operand2.isResult():
        term = operand1.getTerm()
        res = operand2.getResult()
        result = evalOR_term_result(term, res, dictFile, postingsFile)

    # Input 2 is term, Input 1 is result
    elif operand2.isTerm() and operand1.isResult():
        term = operand2.getTerm()
        res = operand1.getResult()
        result = evalOR_term_result(term, res, dictFile, postingsFile)

    # Both inputs are results
    else:
        result1 = operand1.getResult()
        result2 = operand2.getResult()
        result = evalOR_results(result1, result2)

    return Operand(term=None, result=result)


def evalNOT(operand, dictFile, postingsFile):
    """
    input: TermDictionary as dictFile
    input: name of posting file as postingsFle
    output: Operand containing result
    """
    allDocIDs = dictFile.getCorpusDocIDs()
    result = []
    if operand.isTerm():
        # print(operand.getTerm())
        pointerList = dictFile.getTermPointers(operand.getTerm())
        termDocIDs = []
        for pointer in pointerList:
            # print(termDocIDs)
            partialDocIDNodes = retrievePostingsList(postingsFile, pointer)
            termDocIDs.extend([node.getDocID() for node in partialDocIDNodes])
        
        # here, we will have all the docIDs of a term in termDocIDs
        setOfTermDocIDs = set(termDocIDs)
        
    else:  # Operand is result; a list of docIDs
        setOfTermDocIDs = set(operand.getResult())
        
    for ID in allDocIDs:
        if ID not in setOfTermDocIDs:
            result.append(ID)

    return Operand(term=None, result=result)


def evalTerm(term, dictFile, postingsFile):
    """
    Given a term, returns a list of docIDs that contains the term.
    """
    result = []
    pointerList = dictFile.getTermPointers(term.getTerm())
    for pointer in pointerList:
        partialDocIDs = retrievePostingsList(postingsFile, pointer)
        result.extend(partialDocIDs)

    return Operand(term=None, result=result)


def evalOR_terms(term1, term2, dictFile, postingsFile):
    """
    Computes and returns the union of the postings lists of the 2 terms provided.
    """
    result = set()
    pointer1 = dictFile.getTermPointers(term1)
    pointer2 = dictFile.getTermPointers(term2)

    if len(pointer1) == 0 and len(pointer2) > 0: # term1 does not exist in the corpus
        return sorted(set(pointer2))
    elif len(pointer2) == 0 and len(pointer1) > 0: # term2 does not exist in the corpus
        return sorted(set(pointer1))
    elif len(pointer1) == 0 and len(pointer2) == 0: # both term1 and term2 do not exist in the corpus
        return sorted(result)
    
    # else, pointer1 and pointer2 are not empty lists
    termsParsed, i = 0, 0  # termsParsed allows us to check through all chunks, i to obtain the corresponding postings

    while True:
        # Parse postings chunk by chunk, where each chunk is 1024 entries
        if termsParsed <= dictFile.getTermDocFrequency(term1) or termsParsed <= dictFile.getTermDocFrequency(term2):
            if termsParsed <= dictFile.getTermDocFrequency(term1) and termsParsed <= dictFile.getTermDocFrequency(term2):
                pl1 = retrievePostingsList(postingsFile, pointer1[i])
                pl2 = retrievePostingsList(postingsFile, pointer2[i])
            elif termsParsed <= dictFile.getTermDocFrequency(term1):
                pl1 = retrievePostingsList(postingsFile, pointer1[i])
                pl2 = []
            else:
                pl1 = []
                pl2 = retrievePostingsList(postingsFile, pointer2[i])
        else:
            break

        while pl1 != [] or pl2 != []:
            if not pl1:  # if postings list for operand 1 is empty, append that of operand 2 behind
                result.add(Node.getDocID(pl2[0]))
                pl2 = pl2[1:]
            elif not pl2:  # if postings list for operand 2 is empty, append that of operand 1 behind
                result.add(Node.getDocID(pl1[0]))
                pl1 = pl1[1:]
            else:  # Main OR function, union
                result.add(Node.getDocID(pl1[0]))
                result.add(Node.getDocID(pl2[0]))
                pl1, pl2 = pl1[1:], pl2[1:]
        termsParsed += 1024
        i += 1
    return sorted(result)


def evalOR_term_result(term, res, dictFile, postingsFile):
    """
    Computes and returns the union of the postings list of the term and 
    result list provided.
    """
    result = set(res)
    pointer = dictFile.getTermPointers(term)
    if len(pointer) == 0:  # term does not exist in the corpus
        return sorted(result)

    # Retrieve posting lists
    if dictFile.getTermDocFrequency(term) <= 1024:
        nodes = retrievePostingsList(postingsFile, pointer[0])
        pl = [node.getDocID() for node in nodes]
    else:
        pl = []
        for p in pointer:
            nodes = retrievePostingsList(postingsFile, p)
            pl.extend([node.getDocID() for node in nodes])

    # Union both sets
    result.update(set(pl))
    return sorted(result)


def evalOR_results(result1, result2):
    """
    Computes and returns the union of the 2 result list provided.
    """
    result = set(result1)
    result.update(set(result2))  # Union both sets
    return sorted(result)


def evalAND_terms(term1, term2, dictFile, postingsFile):
    """
    Computes and returns the intersection of the postings lists of the 2 terms provided.
    """
    result = set()
    pointer1 = dictFile.getTermPointers(term1)
    pointer2 = dictFile.getTermPointers(term2)

    if len(pointer1) == 0 or len(pointer2) == 0:  # either term1 or term2, or both do not exist in the corpus.
        return sorted(result)

    # else, pointer1 and pointer2 are not empty lists
    termsParsed, i = 0, 0  # termsParsed allows us to check through all chunks, i to obtain the corresponding postings

    while True:
        # Parse postings chunk by chunk, where each chunk is 1024 entries
        if termsParsed <= dictFile.getTermDocFrequency(term1) or termsParsed <= dictFile.getTermDocFrequency(term2):
            if termsParsed <= dictFile.getTermDocFrequency(term1) and termsParsed <= dictFile.getTermDocFrequency(term2):
                pl1 = retrievePostingsList(postingsFile, pointer1[i])
                pl2 = retrievePostingsList(postingsFile, pointer2[i])
            elif termsParsed <= dictFile.getTermDocFrequency(term1):
                pl1 = retrievePostingsList(postingsFile, pointer1[i])
            else:
                pl2 = retrievePostingsList(postingsFile, pointer2[i])
        else:
            break

        while pl1 != [] and pl2 != []:
            if Node.getDocID(pl1[0]) == Node.getDocID(pl2[0]):  # Intersection, add to results
                result.add(Node.getDocID(pl1[0]))
                pl1, pl2 = pl1[1:], pl2[1:]
            else:
                # Advance list with smaller docID
                if Node.getDocID(pl1[0]) < Node.getDocID(pl2[0]):
                    # Check if skip pointers exist, and use if feasible
                    if Node.hasSkip(pl1[0]) and Node.getDocID(pl1[pl1[0].skipPointer]) < Node.getDocID(pl2[0]):
                        pl1 = pl1[pl1[0].skipPointer:]
                    else:
                        pl1 = pl1[1:]
                else:
                    # Check if skip pointers exist, and use if feasible
                    if Node.hasSkip(pl2[0]) and Node.getDocID(pl2[pl2[0].skipPointer]) < Node.getDocID(pl1[0]):
                        pl2 = pl2[pl2[0].skipPointer:]
                    else:
                        pl2 = pl2[1:]
        termsParsed += 1024
        i += 1
    return sorted(result)


def evalAND_term_result(term, res, dictFile, postingsFile):
    """
    Computes and returns the intersection of the postings list of the term and 
    result list provided.
    """
    result = set()
    pointer = dictFile.getTermPointers(term)
    termsParsed, i = 0, 0  # termsParsed allows us to check through all chunks, i to obtain the corresponding postings

    if len(pointer) == 0:  # if term does not exist in the corpus
        return sorted(set())

    # else, pointer1 and pointer2 are not empty lists

    while True:
        # Parse postings chunk by chunk, where each chunk is 1024 entries
        if termsParsed <= dictFile.getTermDocFrequency(term):
            pl = retrievePostingsList(postingsFile, pointer[i])
        else:
            break

        while pl != [] and res != []:
            if Node.getDocID(pl[0]) == res[0]:  # Intersection, add to results
                result.add(res[0])
                pl, res = pl[1:], res[1:]
            else:
                # Advance list with smaller docID
                if Node.getDocID(pl[0]) < res[0]:
                    # Check if skip pointers exist, and use if feasible
                    if Node.hasSkip(pl[0]) and Node.getDocID(pl[pl[0].skipPointer]) < res[0]:
                        pl = pl[pl[0].skipPointer:]
                    else:
                        pl = pl[1:]
                else:
                    res = res[1:]
        termsParsed += 1024
        i += 1

    return sorted(result)


def evalAND_results(result1, result2):
    """
    Computes and returns the intersection of the 2 result list that are provided.
    """
    return sorted(set.intersection(set(result1), set(result2)))


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
