#!/usr/bin/env python3
# pylint: disable=C0111

######################################
#                                    #
# s3550167 - Cary Symes              #
# Information Retrieval Assignment 1 #
# Created 2018-03-27                 #
#                                    #
######################################

from time import time

"""
Timer multifunc
By default takes delta between this time and the last time
Takes a significant amount of time itself - not good for getting the total time
taken to run - good for getting an idea of where the most time is being consumed

Arguments:
    what: String message to tie to this output
    supress: Should we not print?
    store: timer index to store this time in
    ref: timer index to reference this time against
    count: True=add time to reference sum, False=fetch, None=don't sum
"""
def chktm(what=None, surpress=None, store=None, ref=0, count=None):
    # Don't bother with all the stuff if we're not verbose
    # Actually takes a lot of time itself heh
    if chktm.global_supress:
        return 0

    if surpress is None: # default supression gets set by verbosity flag from varargs
        surpress = chktm.global_supress

    now = time()


    if count is False: # output cumulative time
        otm = chktm.counts.get(ref, 0)
    else: # Output referenced time
        otm = now - chktm.bm.get(ref, now)


    if not surpress: # Output time with optional message
        print('{}{}'.format('' if what is None else what + ': ', str(otm)))

    if count is True:
        if ref not in chktm.counts:
            chktm.counts[ref] = 0
        # Add the delta between now and the reference to the counter dict
        chktm.counts[ref] += now - chktm.bm.get(ref, now)

    chktm.bm[0] = now # Last checked time
    if store is not None: # should store this time for later reference
        chktm.bm[store] = now

    return otm

# Perform first-time init
if not hasattr(chktm, 'bm'):
    chktm.bm = {0: time()}  # bookmarks
    chktm.counts = {}       # accumulative run time for a reference
    chktm.global_supress = True # Whether to surpress by default or not - gets overriden by varargs
