# IMPORT FROM PYTHON STANDARD LIBRARY
import ast
import argparse
import datetime
import glob
import logging
#import math
#import operator
import os
import shutil
import subprocess
import sys
import time

from os import path

# IMPORT FROM PROJECT LIBRARY
#from handler import Dir, File

# INITIATE LOGS
LOG = logging.getLogger('log_file')


class Dir:
	""" Base class for system directories """

	def __init__(self, path):
		self._path = None
		self.path = path

	@property
	def path(self):
		return self._path
	
	@path.setter
	def path(self, value):
		if not os.path.isabs(value):
			value = os.path.join(os.getcwd(), value)
		if os.path.isdir(value):
			self._path = value
		else:
			raise NotADirectoryError(value)

	@property
	def dirname(self):
		return self.path.strip("/").split("/")[-1]

	@property
	def children(self):
		children = [Dir(os.path.join(self.path, subdir)) 
			for subdir in os.listdir(self.path) 
			if os.path.isdir(os.path.join(self.path, subdir))]
		if len(children) > 0:
			return children
		else:
			return None

	@property
	def files(self):
		files = [File(os.path.join(self.path, file))
			for file in os.listdir(self.path)
			if os.path.isfile(os.path.join(self.path, file))]
		if len(files) > 0:
			return files
		else:
			return None

	def join(self, *args):
		return os.path.join(self.path, *args)

	def make_subdir(self, *args):
		""" Makes recursive subdirectories from 'os.path.join' like arguments """
		subdir = self.join(*args)
		return self.make(subdir)

	@classmethod
	def make(cls, path):
		try:
			os.makedirs(path)
			return cls(path)
		except FileExistsError:
			return cls(path)

	def __repr__(self):
		return self.path
	
	

class File:
	""" Base class for all file-types """

	def __init__(self, path, file_type=None):
		self._path = None
		self.path = path
		self.file_type = file_type

	@property
	def path(self):
		return self._path
	
	@path.setter
	def path(self, value):
		if not os.path.isabs(value):
			value = os.path.join(os.getcwd(), value)
		if os.path.isfile(value):
			self._path = value
		else:
			raise FileNotFoundError(value)

	@property
	def dir(self):
		return Dir(os.path.dirname(self.path))

	@property
	def filename(self):
		return os.path.basename(self.path)

	@property
	def file_prefix(self):
		return self.filename.split(".")[0]

	@property
	def extension(self):
		return self.filename.split(".")[-1]

	@property
	def write(self, value):
		f = open(os.path, 'a')
		f.write(value)
		f.close()


def configure(args):
	''' Configure base directory, log file, and report file '''
	global BASEDIR, INDIR, LOG, REPORT, TEXT

	# CREATE OUTPUT DIRECTORY
	TOP_DIR = Dir(args.p)
	outDir = '_'.join(('ropro', args.o))
	BASEDIR = TOP_DIR.make_subdir(outDir)

	# GET INDIR
	INDIR = Dir(args.input_directory)

	
	# INITIATE LOG FILE
	#LOG = logging.getLogger('log_file')
	if args.debug:
		LOG.setLevel(logging.DEBUG)
	else:
		LOG.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
	LOG_File = BASEDIR.join("ropro.log")
	file_handler = logging.FileHandler(LOG_File)
	file_handler.setFormatter(formatter)

	LOG.addHandler(file_handler)

	intro = "Running assq."
	LOG.info(f'RUNNING ROPRO.\n Report On PROkka takes data from Prokka and reports the essential information.')
	LOG.info(f'Reporting on data: {INDIR.dirname}\n')
	LOG.info(f'Output will be sent to {BASEDIR.path}\n')


	# INITIATE COMMON TEXT
	TEXT = {}
	TEXT['sectionBreak'] = "\n\n-------------------------------------------------------------\n"
	TEXT['breakSpace'] = "\n\n"

	# INITIATE REPORT FILE
	outFile = '_'.join(('report', args.o))
	outFile = '.'.join((outFile, 'txt'))
	outFile = '/'.join((BASEDIR.path, outFile))
	f = open(outFile, 'w')
	REPORT = File(outFile)
	f.write(f'ROPRO: REPORT ON PROKKA\n\n')
	f.write(f'SAMPLE: {INDIR.dirname}\n')
	f.close()

	LOG.info(f'Generated report file: {REPORT.filename}\n\n')


def check_files(args):
	'''
	Function checks for necessary files
	Necessary files include Prokka generated .txt, .tsv, and .ffn
	If one or more file(s) not found, exit
	'''

	LOG.info('LOOKING FOR INPUT FILES')
	# Make a list of files available in input directory
	fList = {}
	in_f = INDIR.files
	for f in in_f:
		#n = f.filename
		n = f.path
		suffix = f.extension
		if suffix not in fList:
			fList[suffix] = []
			fList[suffix].append(n)
		else:
			fList[suffix].append(n)
		

	suf = ['txt', 'tsv', 'ffn']
	check = True
	for s in suf:
		if s not in fList:
			check = False
			LOG.critical(f'... ERROR. File with suffix {s} was not found.')

	LOG.info('... DONE')
	# Return file list and check status
	return fList, check

def report_results(results, section_name):
	''' 
	Report results 
	
	Input: Function takes a dictionary of statistics and formats the output
	Output: Function appends to the report text file
	'''

	try:
		r = open(REPORT.path, 'a')
		entry = ''.join((TEXT['sectionBreak'], section_name))
		r.write(f'{entry}\n\n')
		for key in results:
			entry = ': '.join((key, str(results[key])))
			r.write(f'{entry}\n')
		r.close()
		LOG.info('... DONE')

	except IOError:
		LOG.error(f'... ERROR. Could not report {section_name}. Skipping.')


def get_stats(in_file):
	''' Extracts values from Prokka text file'''
	# As written, this function only considers the first encountered txt file.
	# TODO: handle multiple text files?

	LOG.info('FETCHING BASIC STATISTICS')
	
	# Extract stats from txt file
	stats = {}
	try:
		f = open(in_file[0], 'r')
		for line in f:
			if ': ' not in line:
				continue
			(key, val) = line.split(': ')
			val = val.replace("\n", "")
			stats[str(key)] = val
		f.close()
	except IOError:
		LOG.critical('... FAILED. Could not open txt file. EXIT')

	LOG.info('... DONE')

	return stats



def calc_functions(in_file):
	''' 
	This function calculates CDS total and percentage by function
	
	Input: Prokka generated .tsv file
	Output: A dictionary of functional annotations and occurances
	'''

	LOG.info('CALCULATING PERCENT BY FUNCTION')

	annotations = ['CDS', 'hypothetical protein', 'putative protein']
	entry = {}
	try:
		f = File(in_file[0])

		# LOOP THROUGH ANNOTATION SEARCH TERMS
		for i in annotations:
			command1 = ['grep', i, f.path]
			command2 = ['wc', '-l']

			process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=False)
			process2 = subprocess.Popen(command2, stdin=process1.stdout, stdout=subprocess.PIPE, shell=False)

			process1.stdout.close()
			process1.wait()
			num = str(process2.communicate()[0])
			num = num.replace("\\n'", '')
			num = num.replace("b'", "")
			num = num.replace(" ", '')
			num = int(num)

			entry[i] = num


	except:
		LOG.error('... ERROR. Could not calculate percent hypothetical protien. Return NA and continue')
		entry['error'] = 'Could not extract genes by function.'
		entry['percent_hypothetical'] = 'NA'
		return entry


	# CALCULATE PERCENT
	if entry['CDS'] == 0:
		entry['percent_hypothetical'] = 'NA'

	else:
		# calculate % of CDS that are hypothetical
		per_hyp = round((entry['hypothetical protein']/entry['CDS'])*100, 2)
		record = ''.join((str(per_hyp), '%'))
		entry['perc_hypothetical'] = record

		# calculate % of CDS that are putative
		per_put = round((entry['putative protein']/entry['CDS'])*100, 2)
		record = ''.join((str(per_put), '%'))
		entry['perc_putative'] = record


	LOG.info('... DONE')
	return entry


def get_sequences(in_file, keyphrases, exact=True):
	''' 
	Extract sequences from a FA file 

	Input: Prokka generated .ffn file
	Output: Dictionary of sequences
	'''

	LOG.info('EXTRACTING SEQUENCES OF INTEREST')

	seqID = []
	entry = {}
	counts = {}

	# INITIATE SEQUENCE DICTIONARY
	for key in keyphrases:
		if key not in entry:
			entry[key] = []
			counts[key] = 'NA'

		# remove duplicate lookup values
		keyphrases[key] = list(dict.fromkeys(keyphrases[key]))	# treats list as dictionary

	# READ INPUT FILE
	try:
		f = File(in_file[0])

		# LOOP THROUGH GENE GROUP
		for key in keyphrases:
			# LOOP THROUGH SEARCH PHRASES FOR GROUP
			for k in keyphrases[key]:
				# get entries containing search phrases
				command1 = ['grep', k, f.path]
				process1 = subprocess.Popen(command1, shell=False, stdout=subprocess.PIPE)
				result = process1.stdout.readlines()
				process1.stdout.close()
				process1.wait()

				# if no result, continue
				if len(result) < 1:
					continue

				# extract sequence ID
				for seqID in result:
					seqID = seqID.decode("utf-8")
					seqID1 = seqID.split()[0]
					seqID2 = seqID1.replace('>', '')
					
					seqName = seqID.replace(seqID1, '').replace('\n', '').lstrip()

					# require an exact match
					if exact == True:
						if seqName != k:
							continue

					# get sequence from ID
					command2 = ['samtools', 'faidx', f.path, seqID2]
					process2 = subprocess.run(command2, capture_output=True)
					
					# format sequence result
					seq = process2.stdout.decode("utf-8")
					seq = seq.replace(seqID1, '')
					seq = seq.replace('\n', '')

					# add result to entry dictionary
					record = [seqID2, seq]
					entry[key].append(record)

		# COUNT NUMBER OF HITS
		for key in entry:
			counts[key] = str(len(entry[key]))

		LOG.info('... DONE')
	
	except:
		LOG.error('... ERROR. Could not extract sequences. Skipping')


	return entry, counts



def export_sequences(args, entry, outName):
	''' 
	Function writes extracted sequences to individual files

	Input: Directory of sequence entries
	Output: An .fa file for each sequence. Compatible with blastn
	'''

	LOG.info('EXPORTING SEQUENCES')

	# CREATE OUTPUT DIRECTORY
	outDirName = ''.join(('seqs_', outName))
	outDir = BASEDIR.make_subdir(outDirName)

	# LOOP THROUGH GENE GROUPS
	for key in entry:
		# LOOP THROUGH SEQUENCE IDENTIFIERS
		for i in entry[key]:

			outFileName = '_'.join((i[0], key))
			outFileName = '.'.join((outFileName, 'fa'))
			outFile = '/'.join((outDir.path, outFileName))

			try:
				f = open(outFile, 'w')
				seqID = ''.join(('>', i[0]))
				out = '\n'.join((seqID, i[1]))
				f.write(out)
				f.close()

			except:
				LOG.error(f'... ERROR. Could not export sequence {i[0]}. Skipping')
				continue

	LOG.info('... DONE')

	return outDir



def align_sequences(args, inDir):
	''' 
	Function runs blastn and reports results

	Input: Directory of .fa files. Each file contains one sequence to align
	Output: Top BLAST alignment hits
	'''

	LOG.info('RUNNING BLAST ALIGNMENTS')

	in_f = inDir.files
	path = args.blastn_path
	outfmt = '7 qseqid stitle pident qcovs qcovhsp length evalue'
	entry = {}

	num_seqs = str(len(in_f))
	LOG.info(f'... Number of sequences that will be aligned: {num_seqs}')

	# ALIGN SEQUENCES IN PROVIDED DIR
	count = 0
	for file in in_f:
		count = count + 1
		LOG.info(f'... ... Aligning sequence {count}')

		seqName = file.file_prefix
		seqID = seqName.split('_')[0]
		# call BLAST remotely
		command = [path, '-remote', '-db', 'nr', '-query', file.path, '-outfmt', outfmt, '-perc_identity', '90', '-qcov_hsp_perc', '95', '-max_target_seqs', '5']
		process = subprocess.run(command, capture_output=True)
		result = process.stdout.decode("utf-8")
		result = ''.join(('\n', result))

		entry[seqName] = result

	LOG.info('... DONE')
	return entry



def count_tRNA(in_file):
	''' 
	Counts the frequency of tRNA by AA and codon

	Input: Prokka generated .tsv file
	Output: Dictionaries reporting number of occurances of tRNAs by AA and codon
	'''

	LOG.info('EXTRACTING tRNA COUNTS')

	# INITIATE tRNA DICTIONARIES
	aa_dict = {
	'Ala':0, 'Arg':0, 'Asn':0, 'Asp':0, 'Cys':0, 
	'Gln':0, 'Glu':0, 'Gly':0, 'His':0, 'Ile':0, 
	'Leu':0, 'Lys':0, 'Met':0, 'Phe':0, 'Pro':0, 
	'Ser':0, 'Thr':0, 'Trp':0, 'Tyr':0, 'Val':0}

	# tRNA codon is reverse complement of sequence
	codon_dict = {
	'aaa':0, 'aac':0, 'aag':0, 'aat':0,
	'aca':0, 'acc':0, 'acg':0, 'act':0,
	'aga':0, 'agc':0, 'agg':0, 'agt':0,
	'ata':0, 'atc':0, 'atg':0, 'att':0,
	'caa':0, 'cac':0, 'cag':0, 'cat':0,
	'cca':0, 'ccc':0, 'ccg':0, 'cct':0,
	'cga':0, 'cgc':0, 'cgg':0, 'cgt':0,
	'cta':0, 'ctc':0, 'ctg':0, 'ctt':0,
	'gaa':0, 'gac':0, 'gag':0, 'gat':0,
	'gca':0, 'gcc':0, 'gcg':0, 'gct':0,
	'gga':0, 'ggc':0, 'ggg':0, 'ggt':0,
	'gta':0, 'gtc':0, 'gtg':0, 'gtt':0,
	'taa':0, 'tac':0, 'tag':0, 'tat':0,
	'tca':0, 'tcc':0, 'tcg':0, 'tct':0,
	'tga':0, 'tgc':0, 'tgg':0, 'tgt':0,
	'tta':0, 'ttc':0, 'ttg':0, 'ttt':0}

	
	entry = {}

	# READ INPUT FILE
	try:
		# GET tRNA ANNOTATIONS
		f = File(in_file[0])
		command = ['grep', '\ttRNA\t', f.path]
		process = subprocess.run(command, capture_output=True)
		result = process.stdout.decode("utf-8").split('\n')

	except:
		LOG.error('... ERROR. Could not open tsv file')
		return entry

	try:
		# EXTRACT AA AND CODON SEQUENCES
		num = 0
		for line in result:
			try:
				if len(line) == 0:
					continue

				num = num + 1
				line = line.split('\t')[6].replace('tRNA-', '').replace(')', '')

				aa = line.split('(')[0]
				codon = line.split('(')[1]

				aa_dict[aa] = aa_dict[aa] + 1
				codon_dict[codon] = codon_dict[codon] + 1
			except:
				continue

	except:
		LOG.error('... ERROR. Cound not extract amino acid and codon sequences.')
		return entry
		

	try:
		# ORGANIZE tRNA BY AA OUTPUT
		count = 0
		sa = '\t\t'
		for aa in aa_dict:
			count = count + 1
			record = ':'.join((aa, str(aa_dict[aa])))
			sa = sa + record
			if count % 5 == 0:
				sa = sa + '\n\t\t\t'
			else:
				sa = sa + '\t'

		# GET tRNA RANGE
		max_key = max(aa_dict.keys(), key=(lambda k: aa_dict[k]))
		min_key = min(aa_dict.keys(), key=(lambda k: aa_dict[k]))
		aa_range = '-'.join((str(aa_dict[min_key]), str(aa_dict[max_key])))
		aa_range = ''.join((aa_range, '\n'))


		# ORGANIZE tRNA BY CODON OUTPUT
		count = 0
		sc =  '\t'
		for co in codon_dict:
			count = count + 1
			record = ':'.join((co, str(codon_dict[co])))
			sc = sc + record
			if count % 4 == 0:
				sc = sc + '\n\t\t\t'
			else:
				sc = sc + '\t'

		# RECORD RESULTS IN DICTIONARY
		entry['tRNAs total'] = str(num)
		entry['tRNAs by AA'] = sa
		entry['tRNA AA range'] = aa_range
		entry['tRNAs by codon'] = sc

	except:
		LOG.error('... ERROR. Cound not format output.')
		return entry


	LOG.info('... DONE')
	return entry



def main(program):
	''' The main worker function to dictate processes '''

	cwd = os.getcwd()

	# PARSER : ROOT
	parent_parser = argparse.ArgumentParser(prog='reportOnProkka', add_help=False)
	parent_parser.add_argument('-b', '--blastn_path', help='Path to blastn', required=True)
	parent_parser.add_argument('-debug', default=False, action='store_true', help='Debug mode; enable debugging output')
	parent_parser.add_argument('-i', '--input_directory', help='Path to input directory')
	parent_parser.add_argument('-o', default="ropro", help='Prefix of output directory', type=str)
	parent_parser.add_argument('-p', default=cwd, help='Path to output', type=str)
	parent_parser.add_argument('-ra', '--run_alignment', default=False, action='store_true', help='Run BLAST alignment on sequences')
	parent_parser.add_argument('--version', action='version', version='%(prog)s 0.0.0')
	subparsers = parent_parser.add_subparsers(help='sub-command help')

	# TODO: Add parser to run Prokka, requires fasta file

	args = parent_parser.parse_args()

	# SET UP
	configure(args)
	fList, check = check_files(args)
	if check != True:
		LOG.info('At least one required file could not be located.')
		LOG.info('Please rerun Prokka or use the run_prokka subprogram')
		exit()

	# GET BASIC ASSEMBLY STATS
	stats = get_stats(fList['txt'])
	LOG.info('REPORTING BASIC ASSEMBLY STATISTICS')
	report_results(stats, 'BASIC ASSEMBLY STATISTICS')


	# CALCULATE THE PERCENT HYPOTHETICAL
	per_hyp = calc_functions(fList['tsv'])
	LOG.info('REPORTING PERCENT BY FUNCTION')
	report_results(per_hyp, 'ANNOTATIONS BY FUNCTION')


	# COUNT tRNAs
	tRNA_counts = count_tRNA(fList['tsv'])
	LOG.info('REPORTING tRNA COUNTS')
	report_results(tRNA_counts, 'tRNA BREAKDOWN')


	# EXTRACT IDENTIFIER SEQUENCES
	identifiers = {'16S': ['16S ribosomal RNA'], 
		'rpoB': ['DNA-directed RNA polymerase subunit beta'], 
		'dnaA': ['Chromosomal replication initiator protein DnaA']}
	ident_seqs, ident_counts = get_sequences(fList['ffn'], identifiers, True)
	LOG.info('REPORTING NUMBER OF IDENTIFIER GENES')
	report_results(ident_counts, 'NUMBER OF IDENTIFIER GENES')


	# EXPORT SEQUENCES
	seq_dir = export_sequences(args, ident_seqs, 'species_identifiers')

	# RUN BLAST ALIGNMENT
	if args.run_alignment == True:
		alignments = align_sequences(args, seq_dir)
		LOG.info('REPORTING BLAST ALIGNMENTS')
		report_results(alignments, 'BLAST ALIGNMENTS')




if __name__== "__main__":
	start_time = time.time()
	main(sys.argv[1])
	LOG.info('\n\tCOMPLETE')
	LOG.info('\n\tEXECUTION TIME: {} seconds'.format(time.time() - start_time))












