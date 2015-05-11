KHMER= ../../khmer

KSIZE= 21
HASH_SIZE= 7e9
N_HASHES= 4

all: estimated_probabilities.${KSIZE}.json

%.fastq.gz:
	wget ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR172/SRR172903/SRR172903.fastq.gz
	wget ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR172/SRR172902/SRR172902.fastq.gz

combined_reads.ht: SRR172902.fastq.gz SRR172903.fastq.gz
	python $(KHMER)/scripts/load-into-counting.py --ksize $(KSIZE) -x $(HASH_SIZE) -N $(N_HASHES) $@ $^

combined_reads_mapping.bam: SRR172902.fastq.gz SRR172903.fastq.gz
	bowtie2 -x mockRefG -U SRR172902.fastq.gz -U SRR172903.fastq.gz | samtools view -S -F4 -b - > combined_reads_mapping.bam

estimated_probabilities.${KSIZE}.json: combined_reads.ht combined_reads_mapping.bam
	python learn.py --json combined_reads.ht combined_reads_mapping.bam > estimated_probabilities.${KSIZE}.json


##############################

MOLECULO_READS=~/galGal/inputs/moleculo

moleculo.combined_reads.ht: $(wildcard $(MOLECULO_READS)/*.fastq.gz)
	python $(KHMER)/scripts/load-into-counting.py --ksize $(KSIZE) -x $(HASH_SIZE) -N $(N_HASHES) $@ $^

moleculo.combined_reads_mapping.bam: $(wildcard $(MOLECULO_READS)/*.fastq.gz)
	bowtie2 -x molReadsG $(foreach READ,$^,$(addprefix ' -U ', $(READ))) | samtools view -S -F4 -b - > combined_reads_mapping.bam

moleculo.estimated_probabilities.${KSIZE}.json: moleculo.combined_reads.ht moleculo.combined_reads_mapping.bam
	python learn.py --json $^ > $@
