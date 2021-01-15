# CodeCommand
# Translates 1 line of VM code into Hack Assembler commands

from constants import *

class CodeCommand:

	def __init__(self, asmfile):
		#asmfile = vmfile.replace(".vm", ".asm")
		self.__asmfile = open(asmfile, 'w')	# Open the asm file and initialize with bootstrapping code
		self.__writelines("@256\n")
		self.__writelines("D=A\n")
		self.__writelines("@SP\n")
		self.__writelines("@M=D\n")
		self.writeGoto("Sys.init")

		# setup global counters
		s = asmfile.split("/")
		s = s[len(s)-1]
		self.__staticvarname = s[:-3] # Save off the root file name without extension with the period for static vars
		self.__labelcnt = 0 # label counter for conditional statements

	

	def close(self):
		self.__asmfile.close()

	def writePush(self, segment, idx):
		self.__asmfile.writelines("//push " + segment + " " + idx + "\n")
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
		self.__asmfile.writelines("//pop " + segment + " " + idx + "\n")
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
		self.__asmfile.writelines("// " + currentCmd + "\n")
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
		
		
	def setFileName(self, Filename):
		pass

	def writeInit(self):
		pass

	def writeLabel(self, Labelname):
		self.__asmfile.writelines("(" + Labelname + ")\n")	

	def writeGoto(self, Labelname):				# Impletements Goto command
		self.__asmfile.writelines("@" + Labelname + "\n")
		self.__asmfile.writelines("0;JMP" + "\n")

	def writeIf(self, Labelname):				# Implements if-goto instruction
	    
		self.__asmfile.writelines("// if-goto " + Labelname + "\n")
		self.__asmfile.writelines("@SP\n")		# decrement the stack pointer
		self.__asmfile.writelines("M=M-1\n")	# decrement the stack		
		self.__asmfile.writelines("@SP\n")		# Pop the condition from the Stack
		self.__asmfile.writelines("A=M\n")											
		self.__asmfile.writelines("D=M\n")											
		self.__asmfile.writelines("@" + Labelname + "\n")	# set the jump to address
		self.__asmfile.writelines("D;JNE" + "\n")# jump if the condition is not 0


	def writeFunction(self, Functionname, localvars):
		self.__asmfile.writelines("(" + Functionname + ")\n")	
		self.__asmfile.writelines("// Setting " + Functionname + " " + localvars + "local variables\n")
		for i in range(int(localvars)):
			self.__asmfile.writelines("@SP\n")		# Push the local variables onto the stack
			self.__asmfile.writelines("A=M\n")
			self.__asmfile.writelines("M=0\n")	
			self.__asmfile.writelines("@SP\n")		# increment the stack pointer
			self.__asmfile.writelines("M=M+1\n")

	def writeCall(self, FunctionName, localvars, vmfile, callidx):
		self.__asmfile.writelines("// call " + FunctionName + " " + localvars + "\n")

		retLabel = vmfile + "." + FunctionName + '$ret.' + callidx
		self.__asmfile.writelines("@" + retLabel + "\n")
		self.__asmfile.writelines("D=A\n")	
		self.__asmfile.writelines("@SP\n")		# push the return address
		self.__asmfile.writelines("A=M\n")	
		self.__asmfile.writelines("M=D\n")	
		self.__asmfile.writelines("@SP\n")		# increment the stack pointer
		self.__asmfile.writelines("M=M+1\n")

		
		self.__asmfile.writelines("@LCL\n")
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@SP\n")		# push LCL of the caller
		self.__asmfile.writelines("A=M\n")
		self.__asmfile.writelines("M=D\n")	
		self.__asmfile.writelines("@SP\n")		# increment the stack pointer
		self.__asmfile.writelines("M=M+1\n")

		self.__asmfile.writelines("@ARG\n")
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@SP\n")		# push ARG of the caller
		self.__asmfile.writelines("A=M\n")
		self.__asmfile.writelines("M=D\n")	
		self.__asmfile.writelines("@SP\n")		# increment the stack pointer
		self.__asmfile.writelines("M=M+1\n")

		self.__asmfile.writelines("@THIS\n")
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@SP\n")		# push THIS of the caller
		self.__asmfile.writelines("A=M\n")
		self.__asmfile.writelines("M=D\n")	
		self.__asmfile.writelines("@SP\n")		# increment the stack pointer
		self.__asmfile.writelines("M=M+1\n")

		self.__asmfile.writelines("@THAT\n")
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@SP\n")		# push THAT of the caller
		self.__asmfile.writelines("A=M\n")
		self.__asmfile.writelines("M=D\n")	
		self.__asmfile.writelines("@SP\n")		# increment the stack pointer
		self.__asmfile.writelines("M=M+1\n")

		self.__asmfile.writelines("@SP\n")		# reposition ARG to SP-5-nArgs
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@5\n")		
		self.__asmfile.writelines("D=D-A\n")
		self.__asmfile.writelines("@" + localvars + "\n")
		self.__asmfile.writelines("D=D-A\n")
		self.__asmfile.writelines("@ARG\n")
		self.__asmfile.writelines("M=D\n")

		self.__asmfile.writelines("@SP\n")		# reposition LCL to SP
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@LCL\n")		
		self.__asmfile.writelines("M=D\n")																			

		self.writeGoto(FunctionName)

		self.writeLabel(retLabel)

	def writeReturn(self):
		self.__asmfile.writelines("// return\n")

		# Set return address to LCL - 5
		self.__asmfile.writelines("@LCL\n")
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@5\n")
		self.__asmfile.writelines("D=D-A\n")
		self.__asmfile.writelines("A=D\n")
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@12\n")		# Register 12 is the temporary local
		self.__asmfile.writelines("M=D\n")	

		# Set ARG to stack value - the return value
		self.__asmfile.writelines("@SP\n")		# decrement the stack pointer
		self.__asmfile.writelines("M=M-1\n")	# decrement the stack		
		self.__asmfile.writelines("@SP\n")		# Pop the condition from the Stack
		self.__asmfile.writelines("A=M\n")											
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@ARG\n")
		self.__asmfile.writelines("A=M\n")	
		self.__asmfile.writelines("M=D\n")
		# Set SP to ARG + 1
		self.__asmfile.writelines("D=A+1\n")
		self.__asmfile.writelines("@SP\n")	
		self.__asmfile.writelines("M=D\n")	

		# Set That to LCL - 1
		self.__asmfile.writelines("@LCL\n")
		self.__asmfile.writelines("A=M-1\n")	
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@THAT\n")
		self.__asmfile.writelines("M=D\n")

		# Set This to LCL - 2
		self.__asmfile.writelines("@2\n")
		self.__asmfile.writelines("D=A\n")
		self.__asmfile.writelines("@LCL\n")
		self.__asmfile.writelines("A=M-D\n")	
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@THIS\n")
		self.__asmfile.writelines("M=D\n")
		# Set ARG to LCL - 3
		self.__asmfile.writelines("@3\n")
		self.__asmfile.writelines("D=A\n")
		self.__asmfile.writelines("@LCL\n")
		self.__asmfile.writelines("A=M-D\n")	
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@ARG\n")
		self.__asmfile.writelines("M=D\n")
		# Set LCL to LCL - 4
		self.__asmfile.writelines("@4\n")
		self.__asmfile.writelines("D=A\n")
		self.__asmfile.writelines("@LCL\n")
		self.__asmfile.writelines("A=M-D\n")	
		self.__asmfile.writelines("D=M\n")
		self.__asmfile.writelines("@LCL\n")
		self.__asmfile.writelines("M=D\n")		
		# goto return address
		self.__asmfile.writelines("@12\n")
		self.__asmfile.writelines("A=M\n")
		self.__asmfile.writelines("0;JMP\n")
		
