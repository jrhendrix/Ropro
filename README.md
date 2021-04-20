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
The number of tRNAs in an assembly can be indicative of assembly completeness and quality. A high quality assembly will have at least one (1 to many) tRNA for each of the 20 AAs (amino acids) (Land, 2014). An assembly with fewer than 20 AAs may be missing genetic content or the annotations may be split accross fragments. Genomes often contain many tRNA genes for each AA, but an excessive number may indicate erronous duplicated content or multiple genomes.

Land et. al examined the number and distribution of tRNAs in 15,000 completed and draft assemblies on GenBank. They found that completed assembies had an average of 55 total tRNAs that represented on average 37 anticodons. The maximum number of unique anticodons identified per genome were 46 in the completed genome set and 47 in the draft genome set. The unrepresented anticodons were overwhelmingly those that started with A (the codon ends with U or T). They use the number of represented AAs (rather than anticodons) in their assessment of genome completion. A genome with fewer than 10 represented AAs was considered to be poor quality.

A quick check of assembly completeness can be done (by looking at the 'tRNA AA range' line) to make sure that each AA is represented by at least one tRNA; however, note that it is not uncommon for an assembly to contain multiple tRNAs for some AAs. If all AAs have 2 or more corresponding tRNAs, consider checking your sample for multiple genomes.

A table of tRNAs by codon is also provided in the report file. It is common the number of tNRAs to be unevenly distributed across the codons. This could be due to reasons that are biological (codon usage bias) or computational (limited resolution for tRNA detection).

See supplementary.md for additional information


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

## References (APA)
Land, M. L., Hyatt, D., Jun, S. R., Kora, G. H., Hauser, L. J., Lukjancenko, O., & Ussery, D. W. (2014). Quality scores for 32,000 genomes. Standards in genomic sciences, 9(1), 1-10.
Seemann, T. (2014). Prokka: rapid prokaryotic genome annotation. Bioinformatics, 30(14), 2068-2069.


