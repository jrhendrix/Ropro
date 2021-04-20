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
The number of tRNAs in an assembly can be indicative of assembly completeness. There are 64 codons that encode for 20 AAs (amino acids) and three stop signals. The potential mathematical range of tRNAs in one organism is 20-62. The minimum of 20 ensures that each of the amino acids are encoded by at least one tRNA. Conversely, a genome could have up 62 tRNAs that each recognize a different anticodon (Land, 2015). One group found that oranisms in the study had an average of 55 tRNAs and a maximum of 284 (Land, 2015). In a study of 30,000 prokaryotic genome sequences, 

In theory, an organism should have at least one tRNA per codon; however, we can see from the Prokka annotations that this is not the case-- each codon may correspond to 0 or multiple tRNA. This could be for two reasons. (1) tRNAs are degenerate and one tNRA can be used to recognize multiple codons and (2) a knowledge gap/lack of resolution.

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
