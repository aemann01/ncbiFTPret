#!/usr/bin/env python3

'''Usage: python ncbiFTPret.py -p /path/to/files -e file.extension [-r True/False]'''

import argparse
from ftplib import FTP
from datetime import datetime
startTime = datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", help="path for download (e.g. /refseq/release/vertebrate_other)", required=True)
parser.add_argument("-e", "--extension", help="file extension for download (e.g. genomic.fna.gz)", required=True)
parser.add_argument("-r", "--recursive", help="use this option if you have nested folders below the extension given", type=bool, default=False)

args = parser.parse_args()

def getFileList():
	host = FTP("ftp.ncbi.nlm.nih.gov", "anonymous", "password")
	host.cwd(args.path)
	print("Connected to ftp.ncbi.nlm.nih.gov\nSuccessfully moved into %s" % args.path)
	full = host.nlst()
	query = []
	for i in full:
		if args.extension in i:
			query.append(i)
		download(query)	

def recursiveDownload():
	host = FTP("ftp.ncbi.nlm.nih.gov", "anonymous", "password")
	host.cwd(args.path)
	print("Connected to ftp.ncbi.nlm.nih.gov\nSuccessfully moved into %s" % args.path)
	full = host.nlst()
	itter = 0
	speciesMap = {}
	print("Preparing to download approximately %i files\n......................" % len(full))
	for directory in full:
		host.cwd(args.path)
		host.cwd(directory)
		second = host.nlst()
		if "representative" in second:
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
						host.retrbinary('RETR ' + i, open(i, 'wb').write)
						print("Processing file %s ... %i of %i species directories" % (i, itter, len(full)))
		else:
			speciesMap[directory] = "noRepFile"					
	with open('speciesMap.csv', 'w') as f:
		[f.write('{0},{1}\n'.format(key, value)) for key, value in speciesMap.items()]

def download():
	print("Preparing to download %i files\n......................" % len(query))
	itter = 1
	for file in query:
		host.retrbinary('RETR ' + file, open(file, 'wb').write)
		print("Processing file %s ... %i of %i" %(file, itter, len(query)))
		itter += 1
	host.quit()	

def main():
	if args.recursive is not None:
		recursiveDownload()
	else:
		getFileList()

main()
print("FTP Connection closed.... task completed in %s" % str(datetime.now() - startTime))