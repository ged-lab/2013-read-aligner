KHMER= ../khmer
DBG_NULL= ../dbg-graph-null/
TRINITY= ~/src/trinity/trinityrnaseq_r20140413p1/Trinity
READ_COV = 100

KSIZE= 30
HASH_SIZE= 4e8
N_HASHES= 4

TRUSTED_CUTOFF= 5
BITS_THETA= 1
DIGINORM_COV= 20

SEQ_FILE = hmp_mock.fastq.gz

all: norm_by_align.fasta.keepalign preload_corrected.fasta.keepalign \
	diginorm_corrected.fasta.keepalign ideal_corrected.fasta.keepalign

.PHONY: all clean

$(SEQ_FILE): SRR172903.fastq.gz SRR172902.fastq.gz
	cat $^ > $@

norm_by_align.fasta.keepalign: $(SEQ_FILE)
	python $(KHMER)/sandbox/normalize-by-align.py --details-out alignment_details.txt --ksize $(KSIZE) -x $(HASH_SIZE) -N $(N_HASHES) -C $(DIGINORM_COV) -t $(TRUSTED_CUTOFF) --bits-theta $(BITS_THETA) -s norm_by_align.ht $< && mv $(SEQ_FILE).keepalign $@ 2>&1 | tee norm_by_align.ht.out 

#read_correction_details.txt: norm_by_align.fasta.keepalign $(SEQ_FILE)
#	../../compare.py mutation_details.txt $(SEQ_FILE) norm_by_align.fasta.keepalign > read_correction_details.txt 2> read_correction_summary.txt

genome.ht: all.fa
	load-into-counting.py --ksize $(KSIZE) -x $(HASH_SIZE) -N $(N_HASHES) $@ $< 2>&1 | tee $@.out 

reads.ht: $(SEQ_FILE)
	load-into-counting.py --ksize $(KSIZE) -x $(HASH_SIZE) -N $(N_HASHES) $@ $< 2>&1 | tee $@.out

diginorm.ht: $(SEQ_FILE)
	normalize-by-median.py -C $(DIGINORM_COV) --ksize $(KSIZE) -x $(HASH_SIZE) -N $(N_HASHES) -s $@ $< 2>&1 | tee $@.out 

preload_corrected.fasta.keepalign: reads.ht $(SEQ_FILE)
	python $(KHMER)/sandbox/read_aligner.py --trusted-cov $(TRUSTED_CUTOFF) --theta $(BITS_THETA) $< $(SEQ_FILE) > $@ 2> preload_alignment_details.txt

#preload_correction_details.txt: preload_corrected.fasta.keepalign $(SEQ_FILE)
#	../../compare.py mutation_details.txt $(SEQ_FILE) $< > $@ 2> preload_correction_summary.txt

diginorm_corrected.fasta.keepalign: diginorm.ht $(SEQ_FILE)
	python $(KHMER)/sandbox/read_aligner.py --trusted-cov $(TRUSTED_CUTOFF) --theta $(BITS_THETA) $< $(SEQ_FILE) > $@ 2> diginorm_alignment_details.txt

diginorm_correction_details.txt: diginorm_corrected.fasta.keepalign $(SEQ_FILE)
	../../compare.py mutation_details.txt $(SEQ_FILE) $< > $@ 2> diginorm_correction_summary.txt

ideal_corrected.fasta.keepalign: genome.ht $(SEQ_FILE)
	python $(KHMER)/sandbox/read_aligner.py --trusted-cov 1 --theta $(BITS_THETA) $< $(SEQ_FILE) > $@ 2> ideal_alignment_details.txt

#ideal_correction_details.txt: ideal_corrected.fasta.keepalign $(SEQ_FILE)
#	../../compare.py mutation_details.txt $(SEQ_FILE) ideal_corrected.fasta.keepalign > $@ 2> ideal_correction_summary.txt

clean:
	-(rm diginorm.ht* norm_by_align.ht* read_correction_details.txt alignment_details.txt mutation_details.txt norm_by_align.fasta.keepalign diginorm_* preload_* ideal_* reads.fasta.keep)

distclean:
	-(rm genome.fasta.gz $(SEQ_FILE) genome.ht* reads.ht* diginorm.ht* norm_by_align.ht* read_correction_details.txt alignment_details.txt mutation_details.txt norm_by_align.fasta.keepalign diginorm_* preload_* ideal_* reads.fasta.keep)

norm_by_align.fasta.keepalign.Trinity.fasta: norm_by_align.fasta.keepalign.pe
	$(TRINITY) --seqType fa --JM 30G --single $< --run_as_paired --output norm_by_align.keepalign --full_cleanup

preload_corrected.fasta.keepalign.Trinity.fasta: preload_corrected.fasta.keepalign.pe
	$(TRINITY) --seqType fa --JM 30G --single $< --run_as_paired --output preload_corrected.keepalign --full_cleanup

# HMP Illumina mock data set http://www.ncbi.nlm.nih.gov/bioproject/48475
%.fastq.gz:
	wget ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR172/SRR172903/SRR172903.fastq.gz
	wget ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR172/SRR172902/SRR172902.fastq.gz
