#!/usr/bin/env python

import sys
import screed
from itertools import izip

def main():
    if len(sys.argv) != 3:
        print >>sys.stderr, "USAGE: correction-compare.py <orig.fasta> <corrected.fasta>"
        sys.exit(1)

    mutations = {}
    orig_reads = {}

    reads_corrected = 0
    nucl_corrected = 0

    for orecord, nrecord in izip(screed.open(sys.argv[1]),
                                 screed.open(sys.argv[2])):
        if orecord["name"] != nrecord["name"]:
            print "Mismatch: {0} {1}".format(orecord["name"], nrecord["name"])
            continue

        if orecord["sequence"] != nrecord["sequence"]:
            reads_corrected +=1
            for pos in range(len(orecord["sequence"])):
                if orecord["sequence"][pos] != nrecord["sequence"][pos]:
                    nucl_corrected +=1

    print "Reads corrected: {0}\nNucleotides corrected: {1}".format(reads_corrected, nucl_corrected)
    
if __name__ == '__main__':
    main()
