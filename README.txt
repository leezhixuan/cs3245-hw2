This is the README file for A0223846B and A0199384J's submission
Email(s): e0564887@u.nus.edu; e0406365@u.nus.edu


== Python Version ==

We're using Python Version 3.8.3 for this assignment.


== General Notes about this assignment ==

— Indexing —
Pre-indexing: 
We check if there exists the working directory we specified. If so, we delete that entire 
directory tree and create a new one in its place. Else, we create the working directory specified. 

Indexing: 
We set a limit, which is the number of documents to be processed at any 1 time. We sort the docIDs in 
the input directory in increasing order, and process them in chunks equivalent to the limit. The ‘process’ 
involves generating a token stream from every document that is in this chunk, and append it to the central 
token stream. Everytime we reach the limit, we make a call to SPIMIInvert(), which creates a dictionary file 
and a postings file in the working directory. In cases where the total number of files is not a multiple of the 
limit we set, an additional call to SPIMIInvert() will always be made to take care of leftover token stream that has been generated.

Upon completing the generation of token streams from all documents in the input directory, we proceed to merge 
them. In our case, a call to binaryMerge() is made, which halves the number of files in the working directory sequentially. 
The binaryMerge() method make calls to mergeDictsAndPostings(). mergeDictsAndPostings() handles the merging of 2 dictionary 
files into a new dictionary file, as well as 2 postings file into a new postings file.

By the end of binaryMerge(), we are left with 1 dictionary file and 1 postings file; both of which are semi-completed products. 
Now, we make a call to implementSkipPointers() with the said postings file as its input. For every postings lists in the posting 
file, we create a Node object for each docID in it, and skip pointers where appropriate [at regular intervals of sqrt(len(postings list)]. 
After skip pointers are added, we save the results into the final postings file. We then create a TermDictionary object with this dictionary file as its input. 

We append the sorted list containing all docIDs in the input directory into the final postings file with no skip pointers added 
(since this information will only be used for the evaluation of complemented terms), and add its pointer into the TermDictionary.

End of Indexing:
We delete the temporary postings file and the working directory that were created to aid the indexing process (SPIMI)
A call to save() is made on the TermDictionary object.

The final format of each postings list is: 
[Node1, Node2, Node2, …], where each Node contains a docID as well as a skip pointer (if any).

The dictionary in the TermDictionary object will be in the form of: 
{term: [docFrequency, pointer], term2: [docFrequency, pointer], ..., "c0rpu5D1r3ct0ry": [all docIDs]}


- Searching -
We preprocess terms in Boolean queries the same way we process words in the corpus. For each
Boolean query, we rely on the Shunting-yard algorithm to turn the query into its post-fix form
(Reverse Polish Notation). We then evaluate this post-fix form with the help of the Operand
class as well as the Stack data structure, and append each query result onto a new line in the results file.
In the case of invalid queries, we output an empty string onto a new line in the results file.

For post-fix form, we depend on "NOT", "AND", and "OR" operators to determine the type of evaluation function to
to run to obtain our result. If the query is purely conjunctive, we run optimisedEvalAND() to 
process terms in ascending order of document frequency, before running evalAND(). Doing so will improve our 
efficiency as it minimises the files we need to search through. 

The evaluation functions that we have are:

= evalNOT =
The docIDs of the entire corpus is saved under "c0rpu5D1r3ct0ry". We retrieve all docIDs of the 
entire corpus and compare them with that of the search term. Every docIDs from the postings list that
belong to "c0rpu5D1r3ct0ry" that are not found in the postings of the search term is added to the result. 
Output is an Operand object that contains a result only, where the result is the resultant postings.

= evalAND =
The general idea of the AND function is as such: The postings of both search terms are
retrieved. With pointers at both starts of the postings, we add the posting to the result if both
posting lists contain said posting. We then advance the list with the smaller docID (both lists
should already be sorted by docID). Another check will be conducted to determine if the taking the skip pointer 
is feasible (i.e. will skip to a posting that is smaller than that of the other posting list), should there be one 
available. Once both lists are fully iterated, the result is output.

There are 3 auxillary functions for this function:
1) evalAND_terms - where both operands are query terms, and posting lists belonging to both will
be retrieved and compared so that we are able to find the common ones between the 2.

2) evalAND_term_result - where one Operand is a search term, and the other being a list of docIDs.
The posting list for the term will be retrieved before it is compared with the other to find the ones
that they share.

3) evalAND_results - where both search terms exists in result form i.e. both are posting lists.
Here, we can simply find the intersection between the 2 postings lists.

Auxillary functions make use of set() to ensure no duplicates and traverse skip pointers accordingly.

Output is an Operand object that contains a result only. The result is a postings list containing all docIDs
common to the 2 input Operands, sorted in ascending order.

= evalOR =
The general idea of the OR function is as such: The postings of both search terms are retrieved. 
Then, we add both postings to a set, which takes care of duplicates.
The union of both postings lists can then be retrieved with ease.

Inputs are Operand objects, which may either be a term or a list of docIDs. If any of the inputs 
are terms, we retrieve their postings lists before passing them into the auxillary function, 
evalOR_results(), as inputs to obtain the result.

There is 1 auxillary function for this function:
evalOR_results - we convert both postings lists into sets so that we are able to obtain the
union of both postings lists with ease.

This auxillary function makes use of the set() property to ensure no duplicates, and the set.union()
function.

Output is an Operand object that contains a result only. The result is a postings list containing all unique docIDs
found in the 2 input Operands, sorted in ascending order.


- Experiments -
1. Having a QueryTerm class
Initally, we were trying to get around the need to evaluate NOT by making use of the QueryTerm class.
This QueryTerm class would contain its term, and whether the term is complemented or not. However, we
realised that having such a class would complicate things, since there would be a mixture of QueryTerm
objects and list of docIDs in the intermediate steps. This would make processing extra tedious. As such,
we evolved the QueryTerm class into the Operand class, where the Operand class can either contain a query
term, or an intermediate result.

2. Optimising "AND NOT" and "OR NOT" queries
We wanted to create additional methods to combine "AND NOT" and "OR NOT" into a single evaluation. While
they may improve the perfomance of searching, we thought the extra code was unnecessary as our
original evaluation process worked fine.

3. Skip pointers
At first, we tried to store the disk location of the destination docID after "skipping". However, it proved
to be too tedious and we ended up storing the distance to skip as a workaround.


== Files included with this submission ==

README.txt - (this), general information about the submission.

index.py - main running code, indexes documents in the corpus with added skip pointers into a postings file via SPIMI, 
and creates a dictionary file.

Node.py - the Node class, the main object type used to store a docID and a skip pointer (if any).

Operand.py - The Operand class, the main object type used to store a query term or a result (a list of docIDs).

search.py - main running code, searches for postings of terms based on boolean queries and outputs the
result to a file.

SPIMI.py - implements SPIMI scalable index construction.

TermDictionary.py - the TermDictionary class, the main object type used to store term information: term,
its document frequency, and the pointer to fetch its postings in the postings file.

dictionary.txt - saved output of dictionary information of TermDictionary: contains terms, their document frequency 
as well as their pointer.

postings.txt - saved output of list of Nodes, where each Node contains a docID and a skip pointer (if any).


== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0223846B and A0199384J, certify that we have followed the CS 3245 Information Retrieval class
guidelines for homework assignments.  In particular, we expressly vow that we have followed the Facebook
rule in discussing with others in doing the assignment and did not take notes (digital or printed) from
the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>


== References ==

Introduction To Information Retrieval - Cambridge University Press (textbook)
https://stackoverflow.com/questions/35067957/how-to-read-pickle-file
https://docs.python.org/3.7/library/pickle.html
https://isaaccomputerscience.org/concepts/dsa_toc_rpn?examBoard=all&stage=all
https://en.wikipedia.org/wiki/Shunting-yard_algorithm
https://stackoverflow.com/questions/1535327/how-to-print-instances-of-a-class-using-print
https://www.tutorialspoint.com/python/file_seek.htm
https://www.w3schools.com/python/ref_file_tell.asp
https://stackoverflow.com/questions/20624682/pickle-dump-replaces-current-file-data
https://docs.python.org/3/library/shutil.html