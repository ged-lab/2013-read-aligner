#!/usr/bin/env python

import pysam
import khmer
import argparse
import collections
from math import log
import json

cigar_to_state = {0: 'M', 1: 'Ir', 2: 'Ig'}


def extract_cigar(cigar):
    ret = []
    for t, length in cigar:
        for i in range(length):
            ret.append(cigar_to_state[t])

    return ret


def trusted_str(cov, trusted_cutoff):
    if cov < trusted_cutoff:
        return '_u'
    else:
        return '_t'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trusted-cutoff', type=int, default=5)
    parser.add_argument(
        "ht", type=str, help="Counting bloom filter for the reads")
    parser.add_argument("bam_file", type=str, help="bam read mapping file")
    parser.add_argument("--json", action='store_true', help="output JSON")

    args = parser.parse_args()

    ht = khmer.load_counting_hash(args.ht)
    samfile = pysam.Samfile(args.bam_file)

    k = ht.ksize()
    seq_cnt = 0
    dropped_seqs = 0
    base_cnt = {}
    state_cnts = {}
    trans_cnts = {}

    total_bases = 0.0

    for rec in samfile:
        seq = rec.seq
        cigar = rec.cigar

        seq_cnt += 1
        if 'N' in seq:
            dropped_seqs += 1
            continue

        states = extract_cigar(cigar)

        kmer = seq[:k]
        state = states[k] + trusted_str(ht.count(kmer), args.trusted_cutoff)

        state_cnts[state] = state_cnts.get(state, 0) + 1
        base_cnt[kmer[-1]] = base_cnt.get(kmer[-1], 0) + 1

        for i in range(1, len(seq) - k - 1):
            total_bases += 1
            kmer = seq[i:i + k]
            cov = ht.get(kmer)

            last_state = state
            state = states[i] + trusted_str(cov, args.trusted_cutoff)

            trans = last_state + '-' + state
            trans_cnts[trans] = trans_cnts.get(trans, 0) + 1

            state_cnts[state] = state_cnts.get(state, 0) + 1
            base_cnt[kmer[-1]] = base_cnt.get(kmer[-1], 0) + 1

    if not args.json:
        print "kmer size=", k
        print "seq count=", seq_cnt, "dropped seqs=", dropped_seqs
        print "base counts=", base_cnt
        print "state counts=", state_cnts
        print "trans counts=", trans_cnts

    
    if not args.json:

        trans_probs = collections.defaultdict(float(0))

        for trans in sorted(trans_cnts.keys()):
            start_state = trans.split('-')[0]
            trans_probs[trans] = trans_cnts[
                trans] / float(state_cnts[start_state])
            print '{0}\t{1:0.7f}'.format(trans, trans_probs[trans])

        print 'static double trans_default[] = { log2{0:0.7f}, log2{1:0.7f}, ' \
            'log2{2:0.7f}, log2{3:0.7f}, log2{4:0.7f}, ' \
            'log2(5:0.7f},'.format(trans_probs['M_t-M_t'],
                                   trans_probs['M_t-Ir_t'],
                                   trans_probs[
                'M_t-Ig_t'], trans_probs['M_t-M_u'],
                trans_probs['M_t-Ir_u'],
                trans_probs['M_t-Ig_u'])
        print 'log2{0:0.7f}, log2{1:0.7f}, log2{2:0.7f}, log2{3:0.7f},'.format(
            trans_probs[
                'Ir_t-M_t'], trans_probs['Ir_t-Ir_t'], trans_probs['Ir_t-M_u'],
            trans_probs['Ir_t,Ir_u'])
        print 'log2{0:0.7f}, log2{1:0.7f}, log2{2:0.7f}, log2{3:0.7f},'.format(
            trans_probs[
                'Ig_t-M_t'], trans_probs['Ig_t-Ig_t'], trans_probs['Ig_t-M_u'],
            trans_probs['Ig_t,Ig_u'])
        print 'log2{0:0.7f}, log2{1:0.7f}, log2{2:0.7f}, log2{3:0.7f}, '\
            'log2{4:0.7f}, log2(5:0.7f},'.format(
                trans_probs['M_u-M_t'], trans_probs['M_u-Ir_t'],
                trans_probs['M_u-Ig_t'], trans_probs['M_u-M_u'],
                trans_probs['M_u-Ir_u'], trans_probs['M_u-Ig_u'])
        print 'log2{0:0.7f}, log2{1:0.7f}, log2{2:0.7f}, log2{3:0.7f},'.format(
            trans_probs[
                'Ir_u-M_t'], trans_probs['Ir_u-Ir_t'], trans_probs['Ir_u-M_u'],
            trans_probs['Ir_u,Ir_u'])
        print 'log2{0:0.7f}, log2{1:0.7f}, log2{2:0.7f}, log2{3:0.7f},'.format(
            trans_probs[
                'Ig_u-M_t'], trans_probs['Ig_u-Ig_t'], trans_probs['Ig_u-M_u'],
            trans_probs['Ig_u,Ig_u'])
        print '};'
    else:
        params = {'scoring_matrix':
                  [-0.06642736173897607,
                   -4.643856189774724,
                   -7.965784284662087,
                   -9.965784284662087],
                  'transition_probabilities': ((
                      log(trans_cnts['M_t-M_t'] / float(state_cnts['M_t']), 2),
                      log(trans_cnts['M_t-Ir_t'] /
                          float(state_cnts['M_t']), 2),
                      log(trans_cnts['M_t-Ig_t'] /
                          float(state_cnts['M_t']), 2),
                      log(trans_cnts['M_t-M_u'] / float(state_cnts['M_t']), 2),
                      log(trans_cnts['M_t-Ir_u'] /
                          float(state_cnts['M_t']), 2),
                      log(trans_cnts['M_t-Ig_u'] /
                          float(state_cnts['M_t']), 2),
                  ), (
                      log(trans_cnts['Ir_t-M_t'] /
                          float(state_cnts['Ir_t']), 2),
                      log(trans_cnts['Ir_t-Ir_t'] /
                          float(state_cnts['Ir_t']), 2),
                      log(trans_cnts['Ir_t-M_u'] /
                          float(state_cnts['Ir_t']), 2),
                      log(trans_cnts['Ir_t-Ir_u'] /
                          float(state_cnts['Ir_t']), 2),
                  ), (
                      log(trans_cnts['Ig_t-M_t'] /
                          float(state_cnts['Ig_t']), 2),
                      log(trans_cnts['Ig_t-Ig_t'] /
                          float(state_cnts['Ig_t']), 2),
                      log(trans_cnts['Ig_t-M_u'] /
                          float(state_cnts['Ig_t']), 2),
                      log(trans_cnts['Ig_t-Ig_u'] /
                          float(state_cnts['Ig_t']), 2),
                  ), (
                      log(trans_cnts['M_u-M_t'] / float(state_cnts['M_u']), 2),
                      log(trans_cnts['M_u-Ir_t'] /
                          float(state_cnts['M_u']), 2),
                      log(trans_cnts['M_u-Ig_t'] /
                          float(state_cnts['M_u']), 2),
                      log(trans_cnts['M_u-M_u'] / float(state_cnts['M_u']), 2),
                      log(trans_cnts['M_u-Ir_u'] /
                          float(state_cnts['M_u']), 2),
                      log(trans_cnts['M_u-Ig_u'] /
                          float(state_cnts['M_u']), 2),
                  ), (
                      log(trans_cnts['Ir_u-M_t'] /
                          float(state_cnts['Ir_u']), 2),
                      log(trans_cnts['Ir_u-Ir_t'] /
                          float(state_cnts['Ir_u']), 2),
                      log(trans_cnts['Ir_u-M_u'] /
                          float(state_cnts['Ir_u']), 2),
                      log(trans_cnts['Ir_u-Ir_u'] /
                          float(state_cnts['Ir_u']), 2),
                  ), (
                      log(trans_cnts['Ig_u-M_t'] /
                          float(state_cnts['Ig_u']), 2),
                      log(trans_cnts['Ig_u-Ig_t'] /
                          float(state_cnts['Ig_u']), 2),
                      log(trans_cnts['Ig_u-M_u'] /
                          float(state_cnts['Ig_u']), 2),
                      log(trans_cnts['Ig_u-Ig_u'] /
                          float(state_cnts['Ig_u']), 2),
                  )
                  )
                  }
        print json.dumps(params, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    main()
