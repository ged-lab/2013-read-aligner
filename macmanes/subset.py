#! /usr/bin/env python
# vim: set fileencoding=UTF-8 :

import sys
from Bio.Blast import NCBIXML

result_handle = open(sys.argv[1])
blast_records = NCBIXML.parse(result_handle)

high_confidence_matches = 0

# "High confidence datasets included only contigs that matched a single
# reference, had sequence similarity >99%, and covered ≥90% of length of
# reference."
# https://peerj.com/articles/113/#table-2
# http://dx.doi.org/10.7717/peerj.113

for record in blast_records:
    if record.alignments and (len(record.alignments) == 1):
        alignment = record.alignments[0]
        threshold = 0.90 * record.query_length
#        if alignment.length >= threshold:
#            identities = 0
#            for hsp in alignment.hsps:
#                identities += hsp.identities
#            if identities > 0.99 * threshold:
        high_confidence_matches += 1

print high_confidence_matches
