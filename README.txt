Prince Hemrajani (s3674204)
Cary Symes       (s3550167)

IR Assignment 2 - Semester 1, 2018

This assignment is written in Python 3.
In order to run it on the coreteaching servers, you will need to enable Python 3 for your current session. This may be done by running the following command:

    scl enable python33 bash

Indexing and querying may then be performed as such:

	python3 index.py [-s <stoplist>] [-p] <collection>
	python3 search.py <ranker> -q <label> -n <# of results> -l <lexicon> -i <invlists> -m <map> [-s <stoplist>] <term 1> [... <term N>]

The advanced IR feature we implemented was option #3, Phrase Search. To this end, <ranker> may be set as either --BM25 or --phrase depending on what method of retrievel is desired. If using phrase search, the number of results need not be specified.