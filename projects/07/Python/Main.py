# Main.py
# Purpose translate vm file to asm instructions

import sys
from constants import *
from Parser import Parser
from CodeCommand import CodeCommand

if len(sys.argv) - 1 > 0:	# check to see if there is a .vm file to parse on the commandline, if so create a Parser
	p = Parser(sys.argv[1])
	c = CodeCommand(sys.argv[1])

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
		if (p.hasMoreCommands == False):
			c.close()
			break
else:
	s = 'this is a not comment // but this is '
	sc = s.split('//')
	print(C_ARITHEMETIC)
