# CodeCommand
# Translates 1 line of VM code into Hack Assembler commands

from constants import *

class CodeCommand:

	def __init__(self, vmfile):
		asmfile = vmfile.replace(".vm", ".asm")
		self.__asmfile = open(asmfile, 'w')
		s = asmfile.split("/")
		s = s[len(s)-1]
		print(s)
		self.__staticvarname = s[:-3] # Save off the root file name without extension with the period
		self.__labelcnt = 0 # label counter for conditional statements

	def close(self):
		self.__asmfile.close()

	def writePush(self, segment, idx):
		#print(segment, idx)
		if (segment == "constant" or segment == "static" or segment == 'pointer'): # there is no index lookup for these memory segment
			if (segment == "constant"):
				self.__asmfile.writelines("@" + idx + '\n')
				self.__asmfile.writelines("D=A\n")
			elif (segment == "pointer"):
				if (idx == '0'):
					self.__asmfile.writelines("@THIS\n")
				else:
					self.__asmfile.writelines("@THAT\n")
				self.__asmfile.writelines("D=M\n")
			else:
				print(segment)
				self.__asmfile.writelines("@" + self.__staticvarname  + idx + '\n') # static variables
				self.__asmfile.writelines("D=M\n")
			self.__asmfile.writelines("@SP\n")
			self.__asmfile.writelines("A=M\n")
			self.__asmfile.writelines("M=D\n")
			self.__asmfile.writelines("@SP\n")
			self.__asmfile.writelines("M=M+1\n")
		else:											# for the other memory segments there is an indexed lookup which requires some addional manipulation
			seg = switcherSegment.get(segment) 			# translate vm segment name to hack segment pointer
			
			self.__asmfile.writelines("@" + idx + '\n')	# load the value of the offset index which is a constant
			self.__asmfile.writelines("D=A\n")
			self.__asmfile.writelines("@" + seg + '\n')	
			if (seg.isnumeric()):						# for temp segment the value passed is base location of the register, not a pointer to it.
				self.__asmfile.writelines("D=D+A\n")
			else:
				self.__asmfile.writelines("D=D+M\n")	
			#self.__asmfile.writelines("D=D+M\n")		# add the offset to the segment address, D now contains the target address to the memory segment
			self.__asmfile.writelines("A=D\n")			# go to the segment address and get the value
			self.__asmfile.writelines("D=M\n")			# D now contains the value from the segment to push to the stack
			self.__asmfile.writelines("@SP\n")
			self.__asmfile.writelines("A=M\n")			# go to the stack memory
			self.__asmfile.writelines("M=D\n")			# set to the value from the memory segment
			self.__asmfile.writelines("@SP\n")			# increment the stack pointer
			self.__asmfile.writelines("M=M+1\n")

	def writePop(self, segment, idx):
		seg = switcherSegment.get(segment) 		# get segment code
		if (seg == "static"):
			self.__asmfile.writelines("@" + self.__staticvarname  + idx + '\n') # static variables
			self.__asmfile.writelines("D=A\n")			# D = mem location to pop the stack to
		elif (seg == "pointer"):
			if (idx == '0'):
				self.__asmfile.writelines("@THIS\n")
			else:
				self.__asmfile.writelines("@THAT\n")
			self.__asmfile.writelines("D=A\n")			# D = mem location to pop the stack to

		else:
			self.__asmfile.writelines("@" + idx + '\n')	# load the value of the offset index
			self.__asmfile.writelines("D=A\n")
			self.__asmfile.writelines("@" + seg + '\n')
			if (seg.isnumeric()):						# for temp segment the value passed is base location of the register, not a pointer to it.
				self.__asmfile.writelines("D=D+A\n")
			else:
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
		
		#print(currentCmd)
		self.__asmfile.writelines("@SP\n")			# decrement the stack pointer
		self.__asmfile.writelines("M=M-1\n")	
		self.__asmfile.writelines("@SP\n")	
		self.__asmfile.writelines("A=M\n")											
		self.__asmfile.writelines("D=M\n")			# place y value in D
		if (currentCmd != 'neg' and currentCmd != 'not'): # these operations only need 1 value from the stack
			self.__asmfile.writelines("@SP\n")			# decrement the stack pointer, 
			self.__asmfile.writelines("M=M-1\n")	
			self.__asmfile.writelines("@SP\n")			
			self.__asmfile.writelines("A=M\n")
													# x value is in M 
		if (currentCmd == 'add'):
			self.__asmfile.writelines("M=M+D\n")	# replace stack value with x + y  
		elif (currentCmd == 'sub'):
			self.__asmfile.writelines("M=M-D\n")	# replace stack value with x - y
		elif (currentCmd == 'and'):
			self.__asmfile.writelines("M=D&M\n")	# replace stack value with y & x  D&M is a supported operation of the ALU not M&D
		elif (currentCmd == 'or'):
			self.__asmfile.writelines("M=D|M\n")	# replace stack value with y | x  D|M is a supported operation of the ALU not M|D
		elif (currentCmd == 'eq' or currentCmd == 'lt' or currentCmd == 'gt'):
			self.__asmfile.writelines("D=M-D\n")
			jump = switcherCondition.get(currentCmd)
			self.__asmfile.writelines("@IF." + str(self.__labelcnt) + "\n")
			self.__asmfile.writelines("D;" + jump + "\n")
			self.__asmfile.writelines("D=0\n")
			self.__asmfile.writelines("@ENDIF." + str(self.__labelcnt) + "\n")
			self.__asmfile.writelines("0;JMP\n")
			self.__asmfile.writelines("(IF." + str(self.__labelcnt) + ")\n")
			self.__asmfile.writelines("D=-1\n")
			self.__asmfile.writelines("(ENDIF." + str(self.__labelcnt) + ")\n")
			self.__asmfile.writelines("@SP\n")	
			self.__asmfile.writelines("A=M\n")	
			self.__asmfile.writelines("M=D\n")
			self.__labelcnt = self.__labelcnt + 1
		elif (currentCmd == "neg"):
			self.__asmfile.writelines("M=-D\n")
		elif (currentCmd == "not"):
			self.__asmfile.writelines("M=!D\n")


		self.__asmfile.writelines("@SP\n")			# increment stack pointer
		self.__asmfile.writelines("M=M+1\n")		
		







		