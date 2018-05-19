#!/usr/bin/env python3
# pylint: disable=C0111

import subprocess
import os

if __name__ == '__main__':
    Q_TOPICS = {}
    Q_REL = {}

    ROOT = 'analytics'

    with open('topics', 'r') as ft:
        for topic in ft:
            topic = topic.split()
            Q_TOPICS[topic[0]] = topic[1:]

    with open('qrels', 'r') as fr:
        for rel in fr:
            rel = rel.split()

            if rel[0] not in Q_REL:
                Q_REL[rel[0]] = {}

            Q_REL[rel[0]][rel[2].lower()] = rel[3] == '1' # Store boolean

    if not os.path.exists(ROOT):
        os.makedirs(ROOT)



    for qn, t in Q_TOPICS.items():
        print(qn, ' '.join(t))


        # BM25 search
        pbm = 'python3 search.py --BM25 -q {} -n 20 -l lexicon -i invlists -m map -s stoplist'
        pbm = pbm.format(qn).split() + t

        rbm = subprocess.check_output(pbm).decode('utf-8').splitlines()
        rbm = rbm[:-1] # Discard time data

        with open('{}/{}_bm25'.format(ROOT, qn), 'w') as bm_out:
            for e in rbm:
                e = e.split()
                bm_out.write('{} {}\n'.format(e[1], e[3]))


        # phrase search
        pph = 'python3 search.py --phrase -q {} -l lexicon -i invlists -m map -s stoplist'
        pph = pph.format(qn).split() + t

        rph = subprocess.check_output(pph).decode('utf-8').splitlines()

        with open('{}/{}_phrase'.format(ROOT, qn), 'w') as ph_out:
            if len(rph) > 3: # Trim unnecessary data
                rph = rph[2:-1]
            else:
                continue # No results found

            for e in rph:
                e = e.split()
                ph_out.write('{} {}\n'.format(e[1], e[2]))
