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

## TODO

* Pull data into summary table for multiple samples

## References
Seemann T. Prokka: rapid prokaryotic genome annotation. Bioin- formatics 2014;30:2068–2069.
