import sys
import os
from os import path

# from constants import *
from JackTokenizer import JackTokenizer


if len(sys.argv) - 1 > 0:	
	

	if (path.isdir(sys.argv[1])):
		print('Process directory...')

		dirname = os.path.basename(os.path.normpath(sys.argv[1]))
		if (dirname == "."):
			dirname = os.path.basename(os.getcwd())


		dirpath = os.path.normpath(sys.argv[1])
		if (dirpath == ""):
			dirpath = os.getcwd()

		jackfiles =[]
		for file in os.listdir(sys.argv[1]):
			if (file.endswith('.jack')):
				jackfiles.append(file)
		

	elif (path.isfile(sys.argv[1])):
		print('Process file...')
		(dirpath, jackfile) = os.path.split(sys.argv[1])
		if (dirpath==""):
			dirpath = os.path.dirname(os.path.realpath(__file__))
		jackfiles = [jackfile]

	else:
		print("Not a valid file or directory")
		jackfiles = []

	print(jackfiles)

	if (len(jackfiles) > 0):

		for f in jackfiles:

			jt = JackTokenizer(dirpath + "/" + f, True) #initialize the Tokenizer
			

			while (jt.hasMoreTokens()):			# begin looping through the .jack file 
				jt.advance()					# process next token
				#print(jt.tokenType)
				
		
