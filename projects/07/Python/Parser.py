# Nand2Tetris
# Parser.py
# Handles the parsing of a single .vm file
# Reads a VM command, parse the command into its lexical components, and provides convenient access to these components
# Ignores all white space and comments
from constants import *

class Parser:

	def __init__(self, vmfile):
		self.__vmfile = open(vmfile, 'r')
		self.__hasMoreCommands = True
		
	def __del__(self):
		self.__vmfile.close()
	

	def advance(self): #Reads the next command from the input and makes it the current command
		# reset internal value
		
		self.__currentCmd = None
		self.__commandType = None
		self.__arg1 = None
		self.__arg2 = None

		# readline
		s = self.__vmfile.readline()
		
		# test whether the end of line -- an empty string -- has been reached, if so, set hasMoreCommands to false
		if (s == ''):
			self.__hasMoreCommands = False
		# test whether new line is \n which is blank
		elif (s == '\n'):
			self.advance()
		else:
			# remove leading and trailing whitespace
			s = s.strip()
			# parse out the inline comments //
			s = s.split('//')
			s = s[0] # only the first part of the line before a comment (//) matters
			# test whether there is anything left after comment removed
			if (s == ''): # this is a full comment line
				self.advance()
			else:
				# inline comments will be stored in the second part of the split and ingnored.
				instruction = s.rstrip() # to remove any trailing whitespace after the split
				# split the line into components
				instruction = instruction.split()	# splits on spaces by default
				# set the properties accordingly
				if len(instruction) >=1: 
					self.__currentCmd = instruction[0]

					self.__commandType = switcher.get(instruction[0])
				if len(instruction) >=2:
					self.__arg1 = instruction[1]
				if len(instruction) >=3:
					self.__arg2 = instruction[2]

	@property
	def hasMoreCommands(self):
		return self.__hasMoreCommands

	@property
	def commandType(self):
		return self.__commandType

	@property
	def arg1(self):
		return self.__arg1

	@property
	def arg2(self):
		return self.__arg2

	@property
	def currentCmd(self):
		return self.__currentCmd

	
	@hasMoreCommands.setter
	def _hasMoreCommands(self, s):
		#s = self.__currentCmd.split()[1]
		self.__hasMoreCommands = s

	@commandType.setter
	def _commandType(self, s):
		#s = self.__currentCmd.split()[1]
		self.__commandType = s

	@arg1.setter
	def _arg1(self, s):
		#s = self.__currentCmd.split()[1]
		self.__arg1 = s

	@arg2.setter
	def _arg2(self, s):
	#s = self.__currentCmd.split()[1]
		self.__arg2 = s

	@currentCmd.setter
	def _currentCmd(self, s):
	#s = self.__currentCmd.split()[1]
		self.__currentCmd = s
		