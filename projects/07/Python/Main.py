# Main.py
# Purpose translate vm file to asm instructions

import sys
import os
from os import path

from constants import *
from Parser import Parser
from CodeCommand import CodeCommand

if len(sys.argv) - 1 > 0:	# check to see if there is a .vm file to parse on the commandline, if so create a Parser
	# Is the path a .vm file or a directory
	

	if (path.isdir(sys.argv[1])):
		print('Process directory...')
		#(dirpath, dirname) = os.path.split(sys.argv[1])
		dirname = os.path.basename(os.path.normpath(sys.argv[1]))
		asmfile = dirname + '.asm'
		dirpath = os.path.normpath(sys.argv[1])
		vmfiles =[]
		for file in os.listdir(sys.argv[1]):
			if (file.endswith('.vm')):
				vmfiles.append(file)
		

	elif (path.isfile(sys.argv[1])):
		print('Process file...')
		(dirpath, vmfile) = os.path.split(sys.argv[1])
		#vmfiles = [os.path.basename(os.path.normpath(sys.argv[1]))]
		vmfiles = [vmfile]
		asmfile = vmfile.replace(".vm", ".asm")

	else:
		print("Not a valid file or directory")
		asmfile = ""
		vmfiles = []

	print(vmfiles)

	if (asmfile != ""):
		c = CodeCommand(dirpath + "/" + asmfile)

		for vmfile in vmfiles:

			p = Parser(dirpath + "/" + vmfile)

			while (True):			# begin looping through the .vm file 
				p.advance()			# code instruction line
				print(p.currentCmd, p.arg1, p.arg2)
				
				if (p.commandType == C_PUSH):
					c.writePush(p.arg1, p.arg2)
				elif (p.commandType == C_POP):
					c.writePop(p.arg1, p.arg2)
				elif (p.commandType == C_ARITHEMETIC):
					c.writeArithmetic(p.currentCmd)
				elif (p.commandType == C_LABEL):
					c.writeLabel(p.arg1)
				elif (p.commandType == C_GOTO):
					c.writeGoto(p.arg1)
				elif (p.commandType == C_IF):
					c.writeIf(p.arg1)
				elif (p.commandType == C_FUNCTION):
					c.writeFunction(p.arg1, p.arg2)
				elif (p.commandType == C_RETURN):
					c.writeReturn()	
				elif (p.commandType == C_CALL):
					c.writeCall(p.arg1, p.arg2, vmfile, '1')	# need to add code to keep track of call history.  use a dictionary to track for example {vmfile.arg1, 1}
				if (p.hasMoreCommands == False):
					break
		c.close()

else:
	s = 'this is a not comment // but this is '
	sc = s.split('//')
	print(C_ARITHEMETIC)
