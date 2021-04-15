# Report On PROkka
This repository contains the scripts for generating a report on Prokka data. This tool is to be used for gathering and reporting data, not for evaluating the results.

## Introduction
Prokka is a bioinformatics tool for annotating bacterial, archaeal, and vial genome assemblies. Output files are generated that contain a lot of information, including the annotation, sequence, and assembly statistics data (Seemann, 2014). The information can be time consuming to mine when there are many samples, but the standard output format of the Prokka software makes it a good candidate for an automated mining system.


## Table of Contents

Table of Contents
0. Run Prokka
1. Record assembly stats
2. Calculate % hypothetical proteins
3. BLAST species identifying genes
4. Plasmid detection

## Usage
Before applying this tool, run [Prokka](https://github.com/tseemann/prokka). 

As input, this script takes a path to the directory of Prokka output.

Example: python ropro.py -i input_directory -o ouput_directory -ra


## Basic Assembly Stats
Displays the statistics presented in the Prokka `.tsv` file and will depend on the run parameters used to run Prokka. For example, non-coding RNAs (ncRNAs) will only be reported if Prokka was run with the `--rfam` parameter.
| Statistic | Description |
| --------- | ----------- |
| contigs | x |
| bases | length of assembly, including all contigs |
| gene | x |
| CDS | x |
| rRNA | x |
| tRNA | x |
| misc_RNA | x |
| tmRNA | x |

## Annotatios by function
The percent hypothetical is an important statistic for determining assembly quality. Due to limitations in current knowlege, there are many bacterial CDS that have not been annotated. Thus, an assembly where 40-60% of CDS are hypothetical proteins may still be a high quality assembly. However, if the percent hypothetical exceeds 90%, the quality/usability should be questioned.

| Statistic | Description |
| --------- | ----------- |
| CDS | x |
| hypothetical protein | x |
| putative protein | x |
| perc_hypothetical | x |
| perc_putative | x |

## tRNA Breakdown
The number of tRNAs in an assembly can be indicative of assembly completeness. There are 64 codons that encode for 20 AAs (amino acids). In theory, an organism should have at least one tRNA per codon; however, we can see from the Prokka annotations that this is not the case-- each codon may correspond to 0 or multiple tRNA. This could be for two reasons. (1) tRNAs are degenerate and one tNRA can be used to recognize multiple codons and (2) a knowledge gap/lack of resolution.

Due to the potential limitaions of reporting the number of tRNAs by codon, the report file also contains a table of the number of tRNAs by AA which seems to be a better indicator of assembly completeness. If an assembly contains fewer than 20 AAs, this could indicate that the assembly is missing content. If an assembly contains multiple tRNAs for every AA, the assembly may contain duplicated content or multiple genomes. A quick check can be done (by looking at the 'tRNA AA range' line) to make sure that each AA is represented by at least one tRNA; however, note that it is not uncommon for an assembly to contain multiple tRNAs for some AAs. 

## Number of identifier genes
The 16S and rpoB genes are commonly used for bacterial species identification because these genes are ubiquitous to bacteria and are species specific. An isolate may contain multiple copies of the 16S gene but bacteria typically only contain one copy of the rpoB gene. Multiple copies of the rpoB gene could indicate sequence duplication or 
Manually finding and extracting these sequences from the `.ffn` file then running a BLAST alignment for each sequence can be labor and time intensive. 

## TODO

* Pull data into summary table for multiple samples

## References
Seemann T. Prokka: rapid prokaryotic genome annotation. Bioin- formatics 2014;30:2068–2069.
