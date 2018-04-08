Prince Hemrajani (s3674204)
Cary Symes       (s3550167)

IR Assignment 1 - Semester 1, 2018

This assignment is written in Python 3.
In order to run it on the coreteaching servers, you will need to enable Python 3 for your current session. This may be done by running the following command:

    scl enable python33 bash

Indexing and querying may then be performed as such:

	python3 index.py [-s <stoplist>] [-p] <collection>
	python3 search.py <lexicon> <invlists> <map> <term 1> [... <term N>]

We also implemented the optional compression extension. The source code for this version may be found in the `src-compression` directory. The code inside may be executed identically to the non-compression version, though the auxiliary files are un-interoperable.