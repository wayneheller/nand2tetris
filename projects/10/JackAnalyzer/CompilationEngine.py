# Handles the compilation of tokens from .jack files into xml in the grammar of the Jack language

from JackTokenizer import JackTokenizer
from Constants import *

class CompilationEngine:

	def __init__(self, jackfile):

		self.tokenizer = JackTokenizer(jackfile, True) #initialize the Tokenizer
		xmlFileName = jackfile[:-5] + "_.xml"
		self.__xmlfile = open(xmlFileName, 'w')
		self.__tabLevel = 0
		self.compileClass()
			
	def __del__(self):
		print("Closing CompilationEngine...")
		self.tokenizer = None

	# these rules do not a compile method:
	# type, className, subroutineName, variableName, statement, subroutineCall

	# class grammar 'class' <className> '{' <classVarDec>* <subroutineDec>* '}'
	def compileClass(self):
		getClassNameNext = False
		getClassVarDecNext = False
		getSubroutineDec = False
		self.writeXML("<class>")
		self.incTabLevel()
		while (self.tokenizer.hasMoreTokens()):		# begin looping through the .jack file 
			self.tokenizer.advance()				# process next token
			if self.tokenizer.currentToken == "class":
				self.writeXML(self.tokenizer.tokenXML)
				getClassNameNext = True
			elif getClassNameNext:
				self.writeXML(self.tokenizer.tokenXML)
				getClassNameNext = False
				getCurlyOpenBracket = True
			elif getCurlyOpenBracket:
				self.writeXML(self.tokenizer.tokenXML)
				getCurlyOpenBracket = False
				getClassVarDecNext = True
			elif getClassVarDecNext or getSubroutineDecNext:
				if self.tokenizer.currentToken in classVarDec: 	# static or field
					self.compileClassVarDec()
				elif self.tokenizer.currentToken in subroutineDec: 	# constructor, function, method
					getClassVarDecNext = False
					getSubroutineDecNext = True
					self.compileSubroutineDec()
				else:
					getSubroutineDec = False
		self.decTabLevel()
		self.writeXML("</class>")

	#  classVarDec grmmar ('static' | 'field') <type> <var-name> (',' <var-name>)* ';'
	def compileClassVarDec(self):
		self.writeXML("<classVarDec>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)	# field or static
		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			self.writeXML(self.tokenizer.tokenXML)
			if self.tokenizer.currentToken == ";":
				break
		self.decTabLevel()
		self.writeXML("</classVarDec>")
		return

	# ('constructor' | 'function' | 'method') ('void' | <type>) <subroutine-name> '(' <parameter-list> ')' <subroutine-body>
	def compileSubroutineDec(self):
		getSubroutineTypeNext = True
		getSubroutineNameNext = False
		getParameterListNext = False
		getClosingParenNext = False
		getSubroutineBodyNext = False
		self.writeXML("<subroutineDec>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)		# ('constructor' | 'function' | 'method')
		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			if getSubroutineTypeNext:
				self.writeXML(self.tokenizer.tokenXML)
				getSubroutineTypeNext = False
				getSubroutineNameNext = True
			elif getSubroutineNameNext:
				self.writeXML(self.tokenizer.tokenXML)
				getSubroutineNameNext = False
				getOpeningParenNext = True
			elif getOpeningParenNext:
				self.writeXML(self.tokenizer.tokenXML)
				getOpeningParenNext = False
				getParameterListNext = True
			elif getParameterListNext:
				self.compileParameterList()
				getParameterListNext = False
				getClosingParenNext = True
			elif getClosingParenNext:
				self.writeXML(self.tokenizer.tokenXML)
				getClosingParenNext = False
				getSubroutineBodyNext = True
			elif getSubroutineBodyNext:
				self.compileSubroutineBody()
				getSubroutineBodyNext = False
				break

		self.decTabLevel()
		self.writeXML("</subroutineDec>")
		return

	def compileParameterList(self):
		pass

	def compileSubroutineBody(self):
		pass

	def compileVarDec(self):
		pass

	def compileStatements(self):
		pass

	def compileLet(self):
		pass

	def compileIf(self):
		pass

	def compileWhile(self):
		pass

	def compileDo(self):
		pass

	def compileReturn(self):
		pass

	def compileTerms(self):
		pass

	def compileExpressionList(self):
		pass

	def errorMsg(self, func, expected, found):
		print("Error in method", func, expected, "was expected", found, "was found.")
		return

	def writeXML(self, s):
		t = "\t" * self.__tabLevel
		self.__xmlfile.writelines(t + s + "\n")
		return

	def incTabLevel(self):
		self.__tabLevel = self.__tabLevel + 1
		return

	def decTabLevel(self):
		self.__tabLevel = self.__tabLevel - 1
		if self.__tabLevel < 1:
			self.__tabLevel = 1
		return