#!/usr/bin/python3
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
    # This is an empty method
    # Pls implement your code in below

    termDict = TermDictionary(dict_file)
    termDict.load()

    with open(queries_file, 'r') as queryFile:
        with open(results_file, 'w') as resultFile:
            allResult = []
            for query in queryFile:
                if query.strip():
                    RPNExpression = shuntingYard(query)
                    result = evaluateRPN(RPNExpression, termDict, postings_file)
                    allResult.append(result)
                else:
                    allResult.append("")

            outputResult = "\n".join(allResult)
            resultFile.write(outputResult)
        resultFile.close()
    queryFile.close()


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
    while(len(operatorStack) > 0):
        output.append(operatorStack.pop())
    return output


def evaluateRPN(RPNexpression, dict_file, postings_file):
    "[X, 'c', 'd', ...]"
    """
    evaluates the input expression (in reverse polish expression) and returns an array of docIDs found
    """
    processStack = [] #enters from the back, exits from the back

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
            operand = Operand(qTerm)
            processStack.append(operand)
    

    # at the end, the processStack will contain just 1 Operand, which could be an array of 
    # result already (in the case where the query is a combination e.g. "hi AND bye"), 
    # or simply just a term (in the case where the query is only 1 word e.g. "hello")

    termOrResult = processStack[0]
    if termOrResult.isTerm():
        processStack.append(evalTerm(processStack.pop(), dict_file, postings_file))

    return " ".join([str(docID) for docID in processStack.pop().getResult()])

        
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


def evalAND(operand1, operand2, dictFile, postingsFile):
    """
    input: TermDictionary as dictFile
    input: name of posting file as postingsFile
    output: Operand containing result
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
    # print("result: ", result)
    return Operand(term=None, result=result)


def evalTerm(term, dictFile, postingsFile):
    result = []
    pointerList = dictFile.getTermPointers(term.getTerm())
    for pointer in pointerList:
        partialDocIDs = retrievePostingsList(postingsFile, pointer)
        result.extend(partialDocIDs)

    return Operand(term=None, result=result)


def evalOR_terms(term1, term2, dictFile, postingsFile):
    result = set()
    pointer1 = dictFile.getTermPointers(term1)
    pointer2 = dictFile.getTermPointers(term2)
    termsParsed, i = 0, 0
    while True:
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
            if not pl1:
                result.add(Node.getDocID(pl2[0]))
                pl2 = pl2[1:]
            elif not pl2:
                result.add(Node.getDocID(pl1[0]))
                pl1 = pl1[1:]
            else:
                result.add(Node.getDocID(pl1[0]))
                result.add(Node.getDocID(pl2[0]))
                pl1, pl2 = pl1[1:], pl2[1:]
        termsParsed += 1024
        i += 1
    return sorted(result)


def evalOR_term_result(term, res, dictFile, postingsFile):
    result = set(res)
    pointer = dictFile.getTermPointers(term)
    if dictFile.getTermDocFrequency(term) <= 1024:
        nodes = retrievePostingsList(postingsFile, pointer[0])
        pl = [node.getDocID() for node in nodes]
    else:
        pl = []
        for p in pointer:
            nodes = retrievePostingsList(postingsFile, p)
            pl.extend([node.getDocID() for node in nodes])
    result.update(set(pl))
    return sorted(result)


def evalOR_results(result1, result2):
    result = set(result1)
    result.update(set(result2))
    return sorted(result)


def evalAND_terms(term1, term2, dictFile, postingsFile):
    result = set()
    pointer1 = dictFile.getTermPointers(term1)
    pointer2 = dictFile.getTermPointers(term2)
    termsParsed, i = 0, 0
    while True:
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
            if Node.getDocID(pl1[0]) == Node.getDocID(pl2[0]):
                result.add(Node.getDocID(pl1[0]))
                pl1, pl2 = pl1[1:], pl2[1:]
            else:
                if Node.getDocID(pl1[0]) < Node.getDocID(pl2[0]):
                    if Node.hasSkip(pl1[0]) and Node.getDocID(pl1[pl1[0].skipPointer]) < Node.getDocID(pl2[0]):
                        pl1 = pl1[pl1[0].skipPointer:]
                    else:
                        pl1 = pl1[1:]
                else:
                    if Node.hasSkip(pl2[0]) and Node.getDocID(pl2[pl2[0].skipPointer]) < Node.getDocID(pl1[0]):
                        pl2 = pl2[pl2[0].skipPointer:]
                    else:
                        pl2 = pl2[1:]
        termsParsed += 1024
        i += 1
    return sorted(result)


def evalAND_term_result(term, res, dictFile, postingsFile):
    set1 = set(res)
    pointer = dictFile.getTermPointers(term)
    if dictFile.getTermDocFrequency(term) <= 1024:
        nodes = retrievePostingsList(postingsFile, pointer[0])
        pl = [node.getDocID() for node in nodes]
    else:
        pl = []
        for p in pointer:
            nodes = retrievePostingsList(postingsFile, p)
            pl.extend([node.getDocID() for node in nodes])
    result = set.intersection(set1, set(pl))
    return sorted(result)


def evalAND_results(result1, result2):
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
