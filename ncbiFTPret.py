#!/usr/bin/env python3

'''Automated download from NCBI FTP server. Can be run recursively if needed. Usage: python ncbiFTPret.py -p /path/to/files -e file.extension [-r True/False -l True/False]'''

import argparse
from ftplib import FTP
from ftplib import FTP, error_perm
from datetime import datetime
startTime = datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", help="path for download (e.g. /refseq/release/vertebrate_other)", required=True)
parser.add_argument("-e", "--extension", help="file extension for download (e.g. genomic.fna.gz)", required=True)
parser.add_argument("-r", "--recursive", help="use this option if you have nested folders below the extension given", type=bool, default=False)
parser.add_argument("-l", "--list", help="retrieves only the file list recursively and writes to file -- can be used to query with wget", type=bool, default=False)

args = parser.parse_args()

def fileList():
	host = FTP("ftp.ncbi.nlm.nih.gov", "anonymous", "password")
	host.cwd(args.path)
	print("Connected to ftp.ncbi.nlm.nih.gov\nSuccessfully moved into %s\n............................" % args.path)
	full = host.nlst()
	dirs = []
	for i in full:
		if ".txt" not in i:
			dirs.append(i)
	files = []
	print(dirs)
	print("%i species folders found" % len(full))
	for directory in dirs:
		host.cwd(args.path)
		host.cwd(directory)
		second = host.nlst()
		if "representative" or "reference" in second:
			host.cwd("representative")
			path = host.pwd()
			third = str(host.nlst()).strip("[").strip("]").strip("'")
			target = str.join("", (str(third).strip("[").strip("]").strip("'"), "_genomic.fna.gz"))
			toadd = str.join("", ("ftp://ftp.ncbi.nlm.nih.gov", path, "/", third, target))
			print(toadd)
		else:
			toadd = str.join("", ("No_representative_folder:", str(directory)))
			print(toadd)
	host.quit()

def singleDirectory():
	host = FTP("ftp.ncbi.nlm.nih.gov", "anonymous", "password")
	host.cwd(args.path)
	print("Connected to ftp.ncbi.nlm.nih.gov\nSuccessfully moved into %s" % str(host.cwd()))
	full = host.nlst()
	query = []
	for i in full:
		if args.extension in i:
			query.append(i)
		download(query)	

def download():
	print("Preparing to download %i files\n......................" % len(query))
	itter = 1
	for file in query:
		host.retrbinary('RETR ' + file, open(file, 'wb').write)
		print("Processing file %s ... %i of %i" %(file, itter, len(query)))
		itter += 1
	host.quit()	

def recursiveDownload():
	host = FTP("ftp.ncbi.nlm.nih.gov", "anonymous", "password")
	host.cwd(args.path)
	print("Connected to ftp.ncbi.nlm.nih.gov\nSuccessfully moved into %s" % args.path)
	full = host.nlst()
	itter = 0
	speciesMap = {}
	print("Preparing to download approximately %i files\n......................" % len([s for s in full if "_" in s]))
	for directory in full:
		host.cwd(args.path)
		host.cwd(directory)
		second = host.nlst()
		if "representative" or "reference" in second:
			host.cwd("representative")
			third = host.nlst()
			speciesMap[directory] = third
			for directory in third:
				if "GC" in directory:
					host.cwd(directory)
					target = host.nlst()
					filt = [i for i in target if args.extension in i]
					filt2 = [i for i in filt if not ('cds' in i or 'rna' in i)]
					for i in filt2:
						itter += 1
						print("Processing file %s ... %i of %i species directories" % (i, itter, len([s for s in full if "_" in s])))
						host.retrbinary('RETR ' + i, open(i, 'wb').write)
		else:
			speciesMap[directory] = "noRepFile"					
	with open('speciesMap.csv', 'w') as f:
		[f.write('{0},{1}\n'.format(key, value)) for key, value in speciesMap.items()]
	host.quit()

def main():
	if args.list == True:
		fileList()
	elif args.recursive == True:
		recursiveDownload()
	else:
		singleDirectory()

main()
print("FTP Connection closed.... task completed in %s" % str(datetime.now() - startTime))