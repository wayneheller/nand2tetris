# CodeCommand
# Translates 1 line of VM code into Hack Assembler commands

from constants import *

class CodeCommand:

	def __init__(self, vmfile):
		asmfile = vmfile.replace(".vm", ".asm")
		self.__asmfile = open(asmfile, 'w')

	def close(self):
		self.__asmfile.close()

	def writePush(self, segment, idx):
		#print(segment, idx)
		if (segment == "constant"):
			self.__asmfile.writelines("@" + idx + '\n')
			self.__asmfile.writelines("D=A\n")
			self.__asmfile.writelines("@SP\n")
			self.__asmfile.writelines("A=M\n")
			self.__asmfile.writelines("M=D\n")
			self.__asmfile.writelines("@SP\n")
			self.__asmfile.writelines("M=M+1\n")
		else:
			seg = switcherSegment.get(segment) 		# get segment code
			
			self.__asmfile.writelines("@" + idx + '\n')		# load the value of the offset index
			self.__asmfile.writelines("D=A\n")
			self.__asmfile.writelines("@" + seg + '\n')		
			self.__asmfile.writelines("D=D+M\n")		# add the offset to the segment address
			self.__asmfile.writelines("A=D\n")			# go to the segment address and get the value
			self.__asmfile.writelines("D=M\n")
			self.__asmfile.writelines("@SP\n")
			self.__asmfile.writelines("A=M\n")			# go to the stack memory
			self.__asmfile.writelines("M=D\n")			# set to the segment value
			self.__asmfile.writelines("@SP\n")			# increment the stack pointer
			self.__asmfile.writelines("M=M+1\n")

	def writePop(self, segment, idx):
		seg = switcherSegment.get(segment) 		# get segment code

		self.__asmfile.writelines("@" + idx + '\n')	# load the value of the offset index
		self.__asmfile.writelines("D=A\n")
		self.__asmfile.writelines("@" + seg + '\n')
		if (seg.isnumeric()):						# for temp segment the value passed is base location of the register, not a pointer to it.
			self.__asmfile.writelines("D=D+A\n")
		self.__asmfile.writelines("D=D+M\n")		# D = mem location to pop the stack to

		self.__asmfile.writelines("@SP\n")			# decrement the stack pointer
		self.__asmfile.writelines("M=M-1\n")	
		
		self.__asmfile.writelines("@SP\n")	
		self.__asmfile.writelines("A=M\n")
		self.__asmfile.writelines("M=M+D\n")		# stack = mem loc + value to pop
		self.__asmfile.writelines("D=M-D\n")		# D has stack value to pop
		self.__asmfile.writelines("A=M-D\n")		# A register points to mem loc
		self.__asmfile.writelines("M=D\n")			# mem loc has  value popped from stack


	def writeArithmetic(self, currentCmd):
		if (currentCmd == 'add' or currentCmd == 'sub'):
			self.__asmfile.writelines("@SP\n")			# decrement the stack pointer
			self.__asmfile.writelines("M=M-1\n")	
			self.__asmfile.writelines("@SP\n")	
			self.__asmfile.writelines("A=M\n")											
			self.__asmfile.writelines("D=M\n")			# place y value in D

			self.__asmfile.writelines("@SP\n")			# decrement the stack pointer, 
			self.__asmfile.writelines("M=M-1\n")	
			self.__asmfile.writelines("@SP\n")			
			self.__asmfile.writelines("A=M\n")
														# x value is in M 
			if (currentCmd == 'add'):
				self.__asmfile.writelines("M=M+D\n")	# replace stack value with x + y  
			else:
				self.__asmfile.writelines("M=M-D\n")	# replace stack value with x - y
			
			self.__asmfile.writelines("@SP\n")			# increment stack pointer
			self.__asmfile.writelines("M=M+1\n")		
		






		