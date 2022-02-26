This is the README file for A0000000X and A0199384J's submission
Email(s): e0564887@u.nus.edu; e0406365@u.nus.edu


== Python Version ==

We're using Python Version <3.7.6 or replace version number> for
this assignment.


== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

- Boolean Queries -
evalNOT - The postings of the entire corpus is saved under "c0rpu5D1r3ct0ry"
This is then compared with the postings for the search term. 
Every posting in "c0rpu5D1r3ct0ry" not in the postings for the search term 
is added to the result. Output is in Operand(term = None, result) object type
where result is the resultant postings.

evalAND - The general idea of the AND function is as such: The postings of 
both search terms are retrieved. With pointers at both starts of the postings,
we add the posting to the result if both posting lists contain said posting.
We then advance the list with the smaller docID (both lists should already be
sorted by docID). Should a skip pointer exist on the posting, another check will
be conducted to determine if the skip pointer is feasible i.e. will skip to a
posting that is smaller than that of the other posting list.
Once both lists are fully iterated, the result is output.
There are 3 auxillary functions for this function:
1) evalAND_terms - where both search terms exist in term form, and posting lists
for both will have to be retrieved.
2) evalAND_term_result - where one search term exists in term form, and the other
is a posting list. The posting list for the term will have to be retrieved before
it is compared with the other.
3) evalAND_results - where both search terms exists in result form i.e. both are
posting lists. Direct comparison can be used.
All three auxillary functions make use of set() to ensure no duplicates, and to use
the set.intersect() function.
Output is in Operand(term = None, result) object type where result is the resultant
postings, which are sorted in ascending order.

evalOR - The general idea of the OR function is as such: The postings of both search
terms are retrieved. 
We iterate through both posting lists and add the postings to the result.
Should one posting list end before the other, the other remaining postings are
appended to the result.
Once both lists are fully iterated, the result is output.
There are 3 auxillary functions for this function:
1) evalOR_terms - where both search terms exist in term form, and posting lists for
both will have to be retrieved.
2) evalOR_term_result - where one search term exists in term form, and the other is
a posting list. The posting list for the term will have to be retrieved before it is
compared with the other.
3) evalOR_results - where both search terms exists in result form i.e. both are
posting lists. Direct comparison can be used.
All three auxillary functions make use of set() to ensure no duplicates, and to use
the set.union() function.
Output is in Operand(term = None, result) object type where result is the resultant
postings, which are sorted in ascending order.


== Files included with this submission ==

README.txt - (this), general information.

index.py - main running code, indexes documents in the corpus with added skip pointers and
scalable index implementation.

search.py - main running code, searches for postings of terms based on boolean queries

dictionary.txt - saved output of dictionary with pointers

postings.txt - saved output of index pointers

Operand.py - for Operand class, the main object type used for processing queries

Node.py - for Node class, the main object type used to store postings

TermDictionary.py - for TermDictionary class, the main object type used to generate the
dictionary


== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0000000X and A0199384J, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>


== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
