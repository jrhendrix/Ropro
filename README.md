# Report On PROkka
Ropro has been moved to Roprokka. Please check out the Roprokka page [here](https://github.com/jrhendrix/Roprokka) for installation and usage instructions.

## Getting Started
On this page can be found an executable version of Roprokka. This version assumes that Samtools and Blast+ are available in your PATH variable.

### Requirements
* Prokka output. Before applying this tool, run [Prokka](https://github.com/tseemann/prokka). 
* samtools 1.5
* blastn 2.10.1+
* python 3.7+

### Usage
```
python ropro.py -i path/to/prokka/output -p path/to/output -o savename
```
