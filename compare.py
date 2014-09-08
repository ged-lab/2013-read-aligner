#!/usr/bin/env python

import sys
import screed

if len(sys.argv) != 4:
    print >>sys.stderr, "USAGE: compare.py <mutations.txt> <orig.fasta> <corrected.fasta>"
    sys.exit(1)

mutations = {}
orig_reads = {}

for line in open(sys.argv[1]):
    lexemes = line.strip().split("\t")
    if len(lexemes) != 4:
        continue

    read_name = lexemes[0]
    pos = int(lexemes[1])
    orig = lexemes[2].upper()
    mut = lexemes[3].upper()

    if read_name not in mutations:
        mutations[read_name] = {}
    mutations[read_name][pos] = {"correct" : orig, "mutation" : mut}

for n, record in enumerate(screed.open(sys.argv[2])):
    orig_reads[record["name"]] = record["sequence"].upper()

tps, fps, tns, fns, tot_errors = 0, 0, 0, 0, 0
print >>sys.stderr, "#read\ttp\tfp\ttn\tfn\ttotal_errors"
for n, record in enumerate(screed.open(sys.argv[3])):
    name = record["name"]
    seq = record["sequence"][:100].upper()
    orig = orig_reads[name]

    read_mut = mutations.get(name, {})
    tp, fp, tn, fn = 0, 0, 0, 0

    for pos in range(len(seq)):
        if pos >= len(orig):
            print >>sys.stderr, "{0}\n{1}\n{2}".format(name, seq, orig)
        if pos in read_mut:
            if seq[pos] == read_mut[pos]["correct"]:
                tp += 1
            else:
                fn += 1
        else:
            if seq[pos] == orig[pos]:
                tn += 1
            else:
                fp += 1

    tps += tp
    fps += fp
    tns += tn
    fns += fn
    tot_errors += len(read_mut)
    print "{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(name, tp, fp, tn, fn, len(read_mut))

print >>sys.stderr, "Totals\t\t{0}\t{1}\t{2}\t{3}\t{4}".format(tps, fps, tns, fns, tot_errors)
