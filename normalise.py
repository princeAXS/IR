#!/usr/bin/env python3
# pylint: disable=C0111

######################################
#                                    #
# s3550167 - Cary Symes              #
# Information Retrieval Assignment 1 #
# Created 2018-03-26                 #
#                                    #
######################################

import re
from string import punctuation as S_PUNC

# Regex matching punctuation from the ASCII char set
DEFAULT_PUNC = '[' + S_PUNC + ']+'

"""
Takes a string and normalises it

Args:
    intake: Input string to be dissected
    hyphens: Boolean - True means replace hyphenated words with a space in the middle
    punctuation: Regex of punctuation marks to be deleted
    case: Boolean - True means fold cases to lowercase
    stops: Set of stop words to ignore

Returns:
    A list (not a set) of the resultant terms
"""
def normalise(intake, hyphens=True, punctuation=DEFAULT_PUNC, case=True, stops=None):
    # Case fold
    if case:
        intake = intake.lower()

    # Replace hyphens
    if hyphens:
        # Match hyphenated words, but /one/ side may be a number
        intake = re.sub(r'(?<=[a-zA-Z])-(?=\w)', ' ', intake)
        intake = re.sub(r'(?<=\w)-(?=[a-zA-Z])', ' ', intake)
        # Otherwise we collapse the hyphen, assuming it's a delimiter
        intake = intake.replace('-', '')
        # That's regex for a hyphen with letters on either side

    # Delete all punc marks from the input string
    if punctuation:
        intake = re.sub(punctuation, ' ', intake)



    if stops:
        # Take terms from the input string if they're not stop words
        terms = [t for t in intake.split() if t not in stops]
    else:
        # Take all terms from the input string
        terms = intake.split()

    return terms
