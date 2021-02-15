# Handles emitting vm code as part of jack file compilation

from Constants import *

class VMWriter:

	def __init__(self, vmFileName):
		self.__vmfile  = open(vmFileName,  'w')
		return
			
	def __del__(self):
		print("Closing VMWriter...")
		self.__vmfile.close()
		return

	def writeFunction(self, className, subroutineName, nLocals):
		self.__vmfile.writelines("function " + className + "." + subroutineName + " " + str(nLocals) + "\n")
		return

	def writePush(self, segmentName, index):
		self.__vmfile.writelines("push " + segmentName + " " + str(index) + "\n")
		return

	def writePop(self, segmentName, index):
		self.__vmfile.writelines("pop " + segmentName + " " + str(index) + "\n")
		return

	def writeArithmetic(self, operator):
		if (operator == "*"):
			self.writeCall("Math.multiply" , 2)
		elif (operator == "/"):
			self.writeCall("Math.divide" , 2)
		else:
			s = switcherOp.get(operator)
			self.__vmfile.writelines(s + "\n")
		return

	def writeUnaryOp(self, operator):
		s = switcherUnaryOp.get(operator)
		self.__vmfile.writelines(s + "\n")
		return


	def writeCall(self, subroutineName, nLocals):
		self.__vmfile.writelines("call " + subroutineName + " " + str(nLocals) + "\n")
		return

	def writeReturn(self):
		self.__vmfile.writelines("return\n")
		return

	def writeIf(self, Label):
		self.__vmfile.writelines("if-goto " + Label + "\n")
		return

	def writeLabel(self, Label):
		self.__vmfile.writelines("label " + Label + "\n")
		return

	def writeGoto(self, Label):
		self.__vmfile.writelines("goto " + Label + "\n")
		return