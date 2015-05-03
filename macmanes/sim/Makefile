KHMER= ../../khmer
DBG_NULL= ../../dbg-graph-null/
TRINITY= ~/src/trinity/trinityrnaseq_r20140413p1/Trinity

READ_COV = 100

KSIZE= 30
HASH_SIZE= 4e8
N_HASHES= 4

HASHPARAMS=--min-tablesize $(HASH_SIZE) --n_tables $(N_HASHES)

TRUSTED_CUTOFF= 5
BITS_THETA= 1
DIGINORM_COV= 20

NCPU=6

SEQ_FILE = sim.reads.fq
$(SEQ_FILE): sim.reads.left.fq.gz sim.reads.right.fq.gz
	interleave-reads.py $< -o $@
sim.reads.left.fq.gz:
	wget -O $@ http://datadryad.org/bitstream/handle/10255/dryad.51511/sim.reads.left.fq.gz?sequence=1
sim.reads.right.fq.gz:
	wget -O $@ http://datadryad.org/bitstream/handle/10255/dryad.51510/sim.reads.right.fq.gz?sequence=2

all: read_correction_summary.txt preload_correction_summary.txt \
	diginorm_correction_summary.txt ideal_correction_summary.txt

.PHONY: all clean

genome.fasta.gz:
	wget ftp://ftp.ensembl.org/pub/release-67/fasta/mus_musculus/dna/Mus_musculus.NCBIM37.67.dna.toplevel.fa.gz
	ln -s Mus_musculus.NCBIM37.67.dna.toplevel.fa.gz $@

norm_by_align.fasta.keepalign: $(SEQ_FILE)
	python $(KHMER)/sandbox/normalize-by-align.py \
		--details-out alignment_details.txt --ksize $(KSIZE) \
		$(HASHPARAMS) -C $(DIGINORM_COV) -t $(TRUSTED_CUTOFF) \
		--bits-theta $(BITS_THETA) -s norm_by_align.ht $< 2>&1 \
		| tee norm_by_align.ht.out && mv $(SEQ_FILE).keepalign $@

genome.ht: genome.fasta.gz
	load-into-counting.py --ksize $(KSIZE) $(HASHPARAMS) \
		$@ $< 2>&1 | tee $@.out 

reads.ht: $(SEQ_FILE)
	load-into-counting.py --ksize $(KSIZE) $(HASHPARAMS) \
		$@ $< 2>&1 | tee $@.out

diginorm.ht: $(SEQ_FILE)
	normalize-by-median.py -C $(DIGINORM_COV) --ksize $(KSIZE) \
		$(HASHPARAMS) -s $@ $< 2>&1 | tee $@.out 

preload_corrected.fasta.keepalign: reads.ht $(SEQ_FILE)
	python $(KHMER)/sandbox/read_aligner.py \
		--trusted-cov $(TRUSTED_CUTOFF) \
		--theta $(BITS_THETA) $^ > $@ 2> preload_alignment_details.txt

correction_summaries = read_correction_summary.txt \
		       preload_correction_summary.txt \
		       diginorm_correction_summary.txt \
		       ideal_correction_summary.txt
$(correction_summaries): %ion_summary.txt: ${SEQ_FILE} %ed.fasta.keepalign
	pypy ../correctioncompare.py $^ | tee $@

diginorm_corrected.fasta.keepalign: diginorm.ht $(SEQ_FILE)
	python $(KHMER)/sandbox/read_aligner.py \
		--trusted-cov $(TRUSTED_CUTOFF) --theta $(BITS_THETA) \
		$^ > $@ 2> diginorm_alignment_details.txt

ideal_corrected.fasta.keepalign: genome.ht $(SEQ_FILE)
	python $(KHMER)/sandbox/read_aligner.py --trusted-cov 1 \
		--theta $(BITS_THETA) $^ > $@ 2> ideal_alignment_details.txt

clean:
	-(rm diginorm.ht* norm_by_align.ht* read_correction_details.txt \
		alignment_details.txt \
		norm_by_align.fasta.keepalign diginorm_* preload_* ideal_* \
		reads.fasta.keep)

distclean: clean
	-(rm genome.fasta.gz $(SEQ_FILE) genome.ht* reads.ht*)

trinity = norm_by_align.Trinity.fasta preload_corrected.Trinity.fasta \
	  diginorm_corrected.Trinity.fasta
$(trinity): %.Trinity.fasta: %.fasta.keepalign
	$(TRINITY) --seqType fa --JM 30G --single $< --run_as_paired \
		--output $(subst .fasta.keepalign,,$<) --full_cleanup \
		--CPU ${NCPU}

trinity_pt = norm_by_align.Trinity.pt preload_corrected.Trinity.pt \
	diginorm_corrected.Trinity.pt uncorr.sim.Trinity.pt
$(trinity_pt): %.pt: %.fasta
	load-graph.py --ksize 26 $(HASHPARAMS) --no-build-tagset \
		--report-total-kmers $(subst .pt,,$@) $< 2> $@.summary
