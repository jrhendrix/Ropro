# Report On PROkka
This repository contains the scripts for generating a report on Prokka data. This tool is to be used for gathering and reporting data, not for evaluating the results.

## Introduction
Prokka is a bioinformatics tool for annotating bacterial, archaeal, and vial genome assemblies. Output files are generated that contain a lot of information, including the annotation list, annotation sequences (nucleic acid and amino acid), and assembly statistics (Seemann, 2014). The information can be time consuming to gather when there are many samples, but the standard output format of the Prokka software makes it a good candidate for an automated mining system.


## Table of Contents

Table of Contents
0. Run Prokka
1. Record assembly stats
2. Calculate % hypothetical proteins
3. BLAST species identifying genes
4. Plasmid detection

## Usage

As input, this script takes a path to the directory of Prokka output.

Example: python ropro.py -ra -i input_directory -o ouput_directory

## Requirements
* Prokka output. Before applying this tool, run [Prokka](https://github.com/tseemann/prokka). 
* samtools 1.5+
* blastn 2.10.1+


## Basic Assembly Stats
Displays the statistics presented in the Prokka `.tsv` file. Note, the statistics reported in this section are entirely dependendent upon the Prokka run parameters. For example, non-coding RNAs (ncRNAs) will only be reported if Prokka was run with the `--rfam` parameter.

| Statistic | Description |
| --------- | ----------- |
| contigs | Number of contigs or segments in the assembly |
| bases | Length of assembly, including all contigs |
| gene | Number of open reading frames identified |
| CDS | Number of coding sequences identified |
| rRNA | Number of ribosomal RNAs identified |
| tRNA | Number of transfer RNAs identified |
| misc_RNA | Number of miscellaneous RNAs identified |
| tmRNA | Number of transfer-messenger RNAs identified |

Note that the CDS and RNA classes are subsets of the genes class.

## Annotatios by function
The percent hypothetical is an important statistic for determining assembly quality. Due to limitations in current knowlege, there are many bacterial CDS that have not been annotated. Thus, an assembly where 40-60% of CDS are hypothetical proteins may still be a high quality assembly. However, if the percent hypothetical exceeds 90%, the quality/usability should be considered.

| Statistic | Description |
| --------- | ----------- |
| CDS | Number of coding sequences identified |
| hypothetical protein | Number of CDS classified as hypothetical |
| putative protein | Number of CDS classified as putative |
| perc_hypothetical | % of CDS classified as hypothetical |
| perc_putative | % of CDS classfied as putative |

## tRNA Breakdown
The number of tRNAs in an assembly can be indicative of assembly completeness and quality (Land, 2014).
In order to express a gene and make a protein, DNA is transcribed into mRNA (messenger RNA) which will contain the reverse compliment sequence where Ts have been replaced with Us). The mRNA is then translated into protein (the Central Dogma of Genetics). 

During translation, the sequence is read in units of three nucleotides, called codons by tRNAs (transfer RNA). The tRNA contains an anticodon sequence on the base which binds to its respective codon on the mRNA. The anticodon is the reverse compliment of the codon which is the reverse compliment of the DNA strand; thus, the tRNA anticodon sequence matches the original DNA seqence, cool huh? The tRNA recognizes its sequence on one end and carries its AA (amino acid) molecule on the other in order to deliver the molecule to the growing AA strand. Thus, the genetic sequence is read and the AA molecule is assembled in the correct order.

Each position can contain one of the four nucleic acids (A, C, G, T/U), giving rise to 64 possible codons (`4^3`). Three of these codons signal for termination of AA production while the rest signal for the addition of one of the 20 AAs. Becasue there are only 20 AAs, one AA could be delivered by multiple tRNAs (where each tRNA recognizes a unique codon). But the number of codons/tRNAs is not the same for each AA. For example, Methionine is only delivered by one tRNA. In contrast, Arginine can be delivered by 6 different tRNAs.

According to Land et. a. 2015, the mathematical range of tRNAs in one organism is 20-62. The minimum of 20 ensures that the organism has at least one way of getting each AA. The maximum of 62 reflects the number of unique anticodons (Land, 2015). NOTE: I propose a different range: 21-64.  The minimum of 21 includes the 20 AAs and one tRNA to stop the AA elongation process. The maximum of 64 reflects the total number of anticodons because the three stop tRNAs recognize different codons. To be efficient, a genome would in theory need to have a number of tRNAs somewhere in this range.

However, biology is not exactly efficient. Land et. al. 2014 examined 30,000 prokaryotic genome sequences available in GenBank. They found a wide range in the number of tRNAs per completed and draft genomes.

Table: % of genomes with n tRNAs per genome
| Num. tRNAs | Complete | Draft |
| ---------- | -------- | ----- |
| 0-40 | 23 | 27 |
| 41-50 | 27 | 23 |
| 51-60 | 21 | 19 |
| 61-70 | 11 | 13 |
| 71-100 | 15 | 16 |
| > 100 | 3 | 1 |
| ----- | -- | -- |
| Min | 7 | 0 |
| Max | 173 | 284 |
| Mean | 55 | 53 |
| N | 2,672 | 12,530 |
| SD | 19 | 20 |


Of 2,672 completed genomes, 23% had fewer than 40 tRNAs, 


They found that many genomes contain a maximum of 280 tRNA genes in a single genome (_Escherichias coli_ HVH 33 (4-2174936))- evidently this genome contains multiple genes for several tRNAs. 

Genomes often contain multiple copies of the same tRNA.
The most anticodons represented were 47.


It is also important to remember the limitations of tRNA detection.

They found that 40% of published genomes were missing at least one tRNA, likely due to fragmentation
They consider a genome with fewer than 10 AA to be of poor quality.




however, we can see from the Prokka annotations that this is not the case-- each codon may correspond to 0 or multiple tRNA. This could be for two reasons. (1) tRNAs are degenerate and one tNRA can be used to recognize multiple codons and (2) a knowledge gap/lack of resolution.

Due to the potential limitaions of reporting the number of tRNAs by codon, the report file also contains a table of the number of tRNAs by AA which seems to be a better indicator of assembly completeness. If an assembly contains fewer than 20 AAs, this could indicate that the assembly is missing content. If an assembly contains multiple tRNAs for every AA, the assembly may contain duplicated content or multiple genomes. A quick check can be done (by looking at the 'tRNA AA range' line) to make sure that each AA is represented by at least one tRNA; however, note that it is not uncommon for an assembly to contain multiple tRNAs for some AAs. 

## Number of Identifier Genes
The 16S rRNA and rpoB genes are commonly used for bacterial species identification because these genes are ubiquitous to bacteria and are species specific. An isolate may contain multiple copies of the 16S gene but bacteria typically only contain one copy of the rpoB gene. Multiple copies of the rpoB gene could indicate sequence duplications or multiple genomes.

## BLAST Alignments
Manually finding and extracting these sequences from the `.ffn` file then running a BLAST alignment for each sequence can be labor and time intensive. Thus, ropro extracts the sequence of each identifier gene and aligns the sequence to the BLASTn database using blastn. Returned are the top 5 BLAST hits that have at least 90% sequence identity and at least 95% coverage of the query sequence. Each hit will have the following field information: 

| Field | Description |
| ----- | ----------- |
| qseqid | query sequence ID |
| stitle | subject title |
| pident | % identity |
| qcovs | % query coverage per subject|
| qcovhsp | % query coverage per hsp |
| length | length of alignment |
| evalue | e value |

The entirety of the BLAST results are returned to the user. This is because a single query might have multiple close matches to related species in the BLAST database. Sometimes distinguishing between these relults are better left to human the human eye.

The sequences for each identifier gene are retained in the output directory in case additional alignments are needed. 

## TODO

* Pull data into summary tsv for multiple samples

## References
Seemann T. Prokka: rapid prokaryotic genome annotation. Bioin- formatics 2014;30:2068–2069.
