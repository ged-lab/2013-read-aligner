KHMER= ../../khmer
DBG_NULL= ../../dbg-graph-null/
TRINITY= ~/src/trinity/trinityrnaseq_r20140413p1/Trinity

READ_COV = 100

KSIZE= 30
HASH_SIZE= 4e8
N_HASHES= 4

TRUSTED_CUTOFF= 5
BITS_THETA= 1
DIGINORM_COV= 20

SEQ_FILE = sim.reads.fq

#all: norm_by_align.fasta.keepalign preload_corrected.fasta.keepalign \
#	diginorm_corrected.fasta.keepalign ideal_corrected.fasta.keepalign

all: read_correction_summary.txt preload_correction_summary.txt \
	diginorm_correction_summary.txt ideal_correction_summary.txt

.PHONY: all clean

$(SEQ_FILE): sim.reads.left.fq.gz sim.reads.right.fq.gz
	interleave-reads.py $< -o $@

genome.fasta.gz:
	wget ftp://ftp.ensembl.org/pub/release-67/fasta/mus_musculus/dna/Mus_musculus.NCBIM37.67.dna.toplevel.fa.gz
	ln -s Mus_musculus.NCBIM37.67.dna.toplevel.fa.gz $@

norm_by_align.fasta.keepalign: $(SEQ_FILE)
	python $(KHMER)/sandbox/normalize-by-align.py --details-out alignment_details.txt --ksize $(KSIZE) -x $(HASH_SIZE) -N $(N_HASHES) -C $(DIGINORM_COV) -t $(TRUSTED_CUTOFF) --bits-theta $(BITS_THETA) -s norm_by_align.ht $< 2>&1 | tee norm_by_align.ht.out && mv $(SEQ_FILE).keepalign $@

#read_correction_details.txt: norm_by_align.fasta.keepalign $(SEQ_FILE)
#	../../compare.py mutation_details.txt $(SEQ_FILE) norm_by_align.fasta.keepalign > read_correction_details.txt 2> read_correction_summary.txt

read_correction_summary.txt: ${SEQ_FILE} norm_by_align.fasta.keepalign
	pypy ../correctioncompare.py $^ | tee $@

genome.ht: genome.fasta.gz
	load-into-counting.py --ksize $(KSIZE) -x $(HASH_SIZE) -N $(N_HASHES) $@ $< 2>&1 | tee $@.out 

reads.ht: $(SEQ_FILE)
	load-into-counting.py --ksize $(KSIZE) -x $(HASH_SIZE) -N $(N_HASHES) $@ $< 2>&1 | tee $@.out

diginorm.ht: $(SEQ_FILE)
	normalize-by-median.py -C $(DIGINORM_COV) --ksize $(KSIZE) -x $(HASH_SIZE) -N $(N_HASHES) -s $@ $< 2>&1 | tee $@.out 

preload_corrected.fasta.keepalign: reads.ht $(SEQ_FILE)
	python $(KHMER)/sandbox/read_aligner.py --trusted-cov $(TRUSTED_CUTOFF) --theta $(BITS_THETA) $< $(SEQ_FILE) > $@ 2> preload_alignment_details.txt

#preload_correction_details.txt: preload_corrected.fasta.keepalign $(SEQ_FILE)
#	../../compare.py mutation_details.txt $(SEQ_FILE) $< > $@ 2> preload_correction_summary.txt

preload_correction_summary.txt: ${SEQ_FILE} preload_corrected.fasta.keepalign
	pypy ../correctioncompare.py $^ | tee $@

diginorm_corrected.fasta.keepalign: diginorm.ht $(SEQ_FILE)
	python $(KHMER)/sandbox/read_aligner.py --trusted-cov $(TRUSTED_CUTOFF) --theta $(BITS_THETA) $< $(SEQ_FILE) > $@ 2> diginorm_alignment_details.txt

#diginorm_correction_details.txt: diginorm_corrected.fasta.keepalign $(SEQ_FILE)
#	../../compare.py mutation_details.txt $(SEQ_FILE) $< > $@ 2> diginorm_correction_summary.txt

diginorm_correction_summary.txt: ${SEQ_FILE} diginorm_corrected.fasta.keepalign
	pypy ../correctioncompare.py $^ | tee $@

ideal_corrected.fasta.keepalign: genome.ht $(SEQ_FILE)
	python $(KHMER)/sandbox/read_aligner.py --trusted-cov 1 --theta $(BITS_THETA) $< $(SEQ_FILE) > $@ 2> ideal_alignment_details.txt

#ideal_correction_details.txt: ideal_corrected.fasta.keepalign $(SEQ_FILE)
#	../../compare.py mutation_details.txt $(SEQ_FILE) ideal_corrected.fasta.keepalign > $@ 2> ideal_correction_summary.txt

ideal_correction_summary.txt: ${SEQ_FILE} ideal_corrected.fasta.keepalign
	pypy ../correctioncompare.py $^ | tee $@

clean:
	-(rm diginorm.ht* norm_by_align.ht* read_correction_details.txt \
		alignment_details.txt \
		norm_by_align.fasta.keepalign diginorm_* preload_* ideal_* \
		reads.fasta.keep)

distclean:
	-(rm genome.fasta.gz $(SEQ_FILE) genome.ht* reads.ht* diginorm.ht* \
		norm_by_align.ht* read_correction_details.txt \
		alignment_details.txt mutation_details.txt \
		norm_by_align.fasta.keepalign diginorm_* preload_* ideal_* \
		reads.fasta.keep)

sim.reads.left.fq.gz:
	wget -O $@ http://datadryad.org/bitstream/handle/10255/dryad.51511/sim.reads.left.fq.gz?sequence=1

sim.reads.right.fq.gz:
	wget -O $@ http://datadryad.org/bitstream/handle/10255/dryad.51510/sim.reads.right.fq.gz?sequence=2

norm_by_align.Trinity.fasta: norm_by_align.fasta.keepalign
	$(TRINITY) --seqType fa --JM 30G --single $< --run_as_paired --output norm_by_align --full_cleanup

preload_corrected.Trinity.fasta: preload_corrected.fasta.keepalign
	$(TRINITY) --seqType fa --JM 30G --single $< --run_as_paired --output preload_corrected --full_cleanup
