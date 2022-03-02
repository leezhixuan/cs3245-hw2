This is the README file for A0223846B and A0199384J's submission
Email(s): e0564887@u.nus.edu; e0406365@u.nus.edu


== Python Version ==

We're using Python Version 3.8.3 for this assignment.


== General Notes about this assignment ==

- Indexing -
First, we sort the documents in the corpus directory according to their docID. Then, we 
apply stemming and case-folding to generate a list of terms for each document in the corpus
directory. We set the max number of docID in each postings list to be 1024, so a new postings
list will be created whenever the current one is full. We store all these information into
a temporary dictionary, which we will use to fill up the TermDictionary class as well as to
write into a temporary postings file (i.e. temp.txt).

Using the information stored in the temporary postings file, we create Nodes for each docID
and add skip pointers where applicable. We then store these nodes into the output posting
file (i.e. postings.txt).

At the end, we add all the docIDs in the corpus into TermDictionary to facilitate the
evaluation of NOT queries and save the information into the specified file (i.e. dictionary.txt).

The information stored in the output dictionary will be in the form of:
{"c0rpu5D1r3ct0ry" : [ALL_DOC_IDs], term1 : [docFreq, [pointer1, pointer2, ...]], 
term2 : [docFreq, [pointer1, pointer2, ...]], ...}

Finally, we delete the temporary postings file (i.e. temp.txt) that was created as a helper.


- Searching -
We preprocess terms in Boolean queries the same way we process words in the corpus. For each
Boolean query, we rely on the Shunting-yard algorithm to turn the query into its post-fix form
(Reverse Polish Notation). We then evaluate this post-fix form with the help of the Operand
class as well as the Stack data structure, and append each query result onto a new line. For
each type of query, we use the identifying terms "NOT", "AND", and "OR" to determine which of
the functions to run to obtain our result. If we identify that the query is purely conjunctive,
we run optimisedEvalAND() to rearrange our stack in ascending order of document frequency, before
running evalAND(). Doing so will improve our efficiency as it minimises the files we need to search
through. 

For each of the base operations, we run the following:

= evalNOT =
The docIDs of the entire corpus is saved under "c0rpu5D1r3ct0ry". This is then compared
with the postings for the search term. Every posting in "c0rpu5D1r3ct0ry" not in the postings
for the search term is added to the result. Output is an Operand that contains a result only,
where the result is the resultant postings.

= evalAND =
The general idea of the AND function is as such: The postings of both search terms are
retrieved. With pointers at both starts of the postings, we add the posting to the result if both
posting lists contain said posting. We then advance the list with the smaller docID (both lists
should already be sorted by docID). Should a skip pointer exist on the posting, another check will
be conducted to determine if the skip pointer is feasible i.e. will skip to a posting that is smaller
than that of the other posting list. Once both lists are fully iterated, the result is output.

There are 3 auxillary functions for this function:
1) evalAND_terms - where both search terms exist in term form, and posting lists for both will have
to be retrieved.
2) evalAND_term_result - where one search term exists in term form, and the other is a posting list.
The posting list for the term will have to be retrieved before it is compared with the other.
3) evalAND_results - where both search terms exists in result form i.e. both are posting lists.
Direct comparison can be used.

All three auxillary functions make use of set() to ensure no duplicates, the set.intersect() function,
and traverse the skip pointers where feasible.

Output is an Operand that contains a result only, where the result is the resultant postings sorted in
ascending order.

= evalOR =
The general idea of the OR function is as such: The postings of both search terms are retrieved. 
Then, we add both postings to a set, which will eliminate any duplicates due to its innate property.
This effectively unions both postings without duplicates. Due to the nature of queries, the inputs may
exist in term form or postings form. As such, we preprocess the terms to extract the postings regardless
of what form they exist in, before calling an auxillary function evalOR_results() to obtain the result.

There is 1 auxillary function for this function:
evalOR_results - we add both postings to the same set so as to remove any duplicates, and obtain the
union of both lists.

This auxillary function makes use of the set() property to ensure no duplicates, and the set.union()
function.

Output is an Operand that contains a result only, where the result is the resultant postings sorted in
ascending order.


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
they may improve the perfomance of searching, we thought it was the extra code was unnecessary as our
original evaluation process worked fine.

3. Skip pointers
At first, we tried to store the disk location of the destination docID after "skipping". However, it proved
to be too tedious and we ended up storing the distance to skip as a workaround.


== Files included with this submission ==

README.txt - (this), general information about the submission.

index.py - main running code, indexes documents in the corpus with added skip pointers and
scalable index implementation: SPIMI.

Node.py - the Node class, the main object type used to store a docID and a skip pointer (if any).

Operand.py - The Operand class, the main object type used to store a query term or a result (a list of docIDs).

search.py - main running code, searches for postings of terms based on boolean queries and outputs the
result to a file.

SPIMI.py - to implement SPIMI scalable index construction.

TermDictionary.py - the TermDictionary class, the main object type used to store term information: term,
its document frequency, and a list of pointers to fetch postings.

dictionary.txt - saved output of dictionary containing terms, their document frequency as well as a list
of pointers.

postings.txt - saved output of Nodes.


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

https://stackoverflow.com/questions/35067957/how-to-read-pickle-file
https://docs.python.org/3.7/library/pickle.html
https://isaaccomputerscience.org/concepts/dsa_toc_rpn?examBoard=all&stage=all
https://en.wikipedia.org/wiki/Shunting-yard_algorithm
https://stackoverflow.com/questions/1535327/how-to-print-instances-of-a-class-using-print
https://www.tutorialspoint.com/python/file_seek.htm
https://www.w3schools.com/python/ref_file_tell.asp
