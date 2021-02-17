# Handles the creation and manipulation of symbol tables for the compiler

from Constants import *

class SymbolTable:

	def __init__(self):
		self.__dictType = {}
		self.__dictKind = {}
		self.__dictIndex = {}
		return
	
			
	def __del__(self):
		print("Closing SymbolTable...")
		
	def startSubroutine(self):
		#print("clearing subroutine symbol table")
		self.__dictType.clear()
		self.__dictKind.clear()
		self.__dictIndex.clear()

	def define(self, name, symType, kind):				# if name does not existin in the symbol table, add it and return True, else return False
		if (self.__dictType.get(name) == None):
			self.__dictType.update({name : symType})
			self.__dictIndex.update({name : self.VarCount(kind)})
			self.__dictKind.update({name : kind})
			return True
		else:
			return False

	def VarCount(self, kind):
		return sum(x == kind for x in self.__dictKind.values()) 
		
	def KindOf(self, name):						# field static augument local
		return self.__dictKind.get(name)

	def TypeOf(self, name):						# int boolean String ...
		return self.__dictType.get(name)

	def IndexOf(self, name):
		return self.__dictIndex.get(name)


