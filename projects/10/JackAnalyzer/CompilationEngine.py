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
				if self.tokenizer.currentToken == "(":
					self.writeXML(self.tokenizer.tokenXML)
					getParameterListNext = True
					getOpeningParenNext = False
				else:
					self.errorMsg("compileSubroutineDec", "(", self.tokenizer.currentToken)
				
			elif getParameterListNext:
				# test for whether there is a parameter List
				if self.tokenizer.currentToken != ")":
					self.compileParameterList()
				self.writeXML(self.tokenizer.tokenXML)  # closing paren )
				getParameterListNext = False
				getSubroutineBodyNext = True
				
			elif getSubroutineBodyNext:
				self.compileSubroutineBody()
				getSubroutineBodyNext = False
				break

		self.decTabLevel()
		self.writeXML("</subroutineDec>")
		return

	# Parameter List Grammar ( <type> <var-name> (',' <type> <var-name>)* )?
	def compileParameterList(self):
		self.writeXML("<parameterList>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)	
		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			self.writeXML(self.tokenizer.tokenXML)
			if self.tokenizer.currentToken == ")":
				break
		self.decTabLevel()
		self.writeXML("</parameterList>")
		return

	# subroutine Body Grammar; <subroutine-body> '{' <var-dec>* <statements> '}'
	def compileSubroutineBody(self):
		self.writeXML("<subroutineBody>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)		# {
		getVarDecNext = True
		getStatementsNext = False
		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			if getVarDecNext:
				if self.tokenizer.currentToken == "var":
					self.compileClassVarDec()
				getVarDecNext = False
				getStatementsNext = True
			if getStatementsNext == True:
				self.compileStatements()
				self.writeXML(self.tokenizer.tokenXML) # }
				break

		self.decTabLevel()
		self.writeXML("</subroutineDec>")
		return

	# Var Dec Grammar; 'var' <type> <var-name> (',' <var-name>)* ';'
	def compileVarDec(self):
		self.writeXML("<varDec>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)	
		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			self.writeXML(self.tokenizer.tokenXML)
			if self.tokenizer.currentToken == ";":
				break
		self.decTabLevel()
		self.writeXML("</varDec>")

	# statement Grammar: (<let-statement> | <if-statement> | <while-statement> | <do-statement> | <return-statement>)*
	def compileStatements(self):
		self.writeXML("<statements>")
		self.incTabLevel()
		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			if self.tokenizer.currentToken == "let":
				self.compileLet()
			elif self.tokenizer.currentToken == "if":
				self.compileIf()
			elif self.tokenizer.currentToken == "while":
				self.compileWhile()
			elif self.tokenizer.currentToken == "do":
				self.compileDo()
			elif self.tokenizer.currentToken == "return":
				self.compileReturn()
			elif self.tokenizer.currentToken == "}":
				break

		self.decTabLevel()
		self.writeXML("</statements>")

	# let statement grammar; 'let' <var-name> ('[' <expression> ']')? '=' <expression> ';'
	def compileLet(self):
		self.writeXML("<letStatement>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)	 # let

		getVarNameNext = True
		getVarExpressionNext = False
		getClosedSquareBracketNext = False
		getEqualSignNext = False
		getExpressionNext = False
		getSemicolonNext = False

		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			if getVarNameNext:
				#print("varName", self.tokenizer.currentToken)
				self.writeXML(self.tokenizer.tokenXML)
				getVarNameNext = False
				getVarExpressionNext = True
			elif getVarExpressionNext:
				if self.tokenizer.currentToken == "[":
					self.writeXML(self.tokenizer.tokenXML)
					self.compileExpression()
					self.writeXML(self.tokenizer.tokenXML) # ]
					getEqualSignNext = True

				elif self.tokenizer.currentToken == "=":
					#print("Equal", self.tokenizer.currentToken)
					self.writeXML(self.tokenizer.tokenXML)
					getExpressionNext = True
					getEqualSignNext = False

				getVarExpressionNext = False
				
			elif getEqualSignNext:
				if self.tokenizer.currentToken == "=":
					print("=", self.tokenizer.currentToken)
					self.writeXML(self.tokenizer.tokenXML)
					getExpressionNext = True
					getEqualSignNext = False
				else:
					self.errorMsg("compileLet", "=", self.tokenizer.currentToken)

			elif getExpressionNext:
				self.compileExpression()
				getExpressionNext = False
				getSemicolonNext = True

			elif getSemicolonNext:
				if self.tokenizer.currentToken == ";":
					self.writeXML(self.tokenizer.tokenXML)
					#print("break")
					break
				else:
					self.errorMsg("compileLet", ";", self.tokenizer.currentToken)
		
		self.decTabLevel()
		self.writeXML("</letStatement>")

	def compileIf(self):
		pass

	def compileWhile(self):
		pass

	def compileDo(self):
		pass

	def compileReturn(self):
		pass

	def compileExpression(self):
		return

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