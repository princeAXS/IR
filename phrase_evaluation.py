#!/usr/bin/env python3
# pylint: disable=C0111,C0326

######################################
#                                    #
# s3550167 - Cary Symes              #
# Information Retrieval Assignment 2 #
# Created 2018-05-19                 #
#                                    #
######################################

import subprocess
import os

if __name__ == '__main__':
    Q_TOPICS = {}
    Q_REL = {}

    SRC_ROOT = './'
    ROOT = 'analytics'

    RESULTS_BM25   = {}
    RESULTS_PHRASE = {}

    BM25_SIZE = 20
    PRECISION = 10

    STALE = True

    with open(SRC_ROOT + 'topics', 'r') as ft:
        for topic in ft:
            topic = topic.split()
            Q_TOPICS[topic[0]] = topic[1:]

    with open(SRC_ROOT + 'qrels', 'r') as fr:
        for rel in fr:
            rel = rel.split()

            if rel[0] not in Q_REL:
                Q_REL[rel[0]] = {}

            Q_REL[rel[0]][rel[2].lower()] = rel[3] == '1' # Store boolean

    if not os.path.exists(ROOT):
        os.makedirs(ROOT)

    for qn, t in Q_TOPICS.items():
        print(qn, ' '.join(t))

        # Perform BM25 searches
        pbm = 'python3 search.py --BM25 -q {} -n {} -l lexicon -i invlists -m map -s stoplist'
        pbm = pbm.format(qn, BM25_SIZE).split() + t

        rbm = subprocess.check_output(pbm).decode('utf-8').splitlines() # Call search.py
        rbm = rbm[:-1] # Discard time data

        data = []
        for e in rbm:
            e = e.split()
            data.append( (e[1], e[3]) ) # Extract needed data
        RESULTS_BM25[qn] = data # Store for later use

        # Calculate P@10
        REL = Q_REL[qn]
        RESULTS = RESULTS_BM25[qn][0:PRECISION]

        # Get the number of relevant documents in this query
        # Account for un-rated results (there are 14 spread across the BM25 results)
        rel_ans = sum([1 if (doc[0] in REL and REL[doc[0]]) else 0 for doc in RESULTS])
        precision_bm = rel_ans/(len(RESULTS) or 1) # Cater for a divide by zero



        # phrase searches
        pph = 'python3 search.py --phrase -q {} -l lexicon -i invlists -m map -s stoplist'
        pph = pph.format(qn).split() + t

        rph = subprocess.check_output(pph).decode('utf-8').splitlines()
        rph = rph[:-1] # Trim timing data

        data = []
        for e in rph:
            e = e.split()
            data.append( (e[1], e[2]) )
        RESULTS_PHRASE[qn] = data

        # Calculate P@10
        REL = Q_REL[qn]
        RESULTS = RESULTS_PHRASE[qn][0:PRECISION]

        # Get the number of relevant documents in this query
        rel_ans = sum([1 if (doc[0] in REL and REL[doc[0]]) else 0 for doc in RESULTS])
        precision_ph = rel_ans/(len(RESULTS) or 1)





        print('BM25   # Results: {}'.format(len(RESULTS_BM25[qn])))
        print('BM25   Precision: {}'.format(precision_bm))
        print('Phrase # Results: {}'.format(len(RESULTS_PHRASE[qn])))
        print('Phrase Precision: {}'.format(precision_ph))
        print()


        if STALE:
            # Save results to disk
            with open('{}/{}_phrase'.format(ROOT, qn), 'w') as ph_out:
                for e in RESULTS_PHRASE[qn]:
                    REL = Q_REL[qn]
                    ph_out.write('{} {} {}\n'.format(*(e + (1 if (e[0] in REL and REL[e[0]]) else 0,))))

            with open('{}/{}_bm25'.format(ROOT, qn), 'w') as bm_out:
                for e in RESULTS_BM25[qn]:
                    REL = Q_REL[qn]
                    bm_out.write('{} {} {}\n'.format(*(e + (1 if (e[0] in REL and REL[e[0]]) else 0,))))
