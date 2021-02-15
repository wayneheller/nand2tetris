# Handles the compilation of tokens from .jack files into xml in the grammar of the Jack language

from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter
from Constants import *

class CompilationEngine:

	def __init__(self, jackfile):

		self.tokenizer = JackTokenizer(jackfile, True) #initialize the Tokenizer
		xmlFileName = jackfile[:-5] + "_.xml"
		self.__xmlfile = open(xmlFileName, 'w')

		vmFileName  = jackfile[:-5] + ".vm"
		self.vmWriter = VMWriter(vmFileName)
		
		self.__tabLevel = 0
		self.__clsSymTable = SymbolTable()		# symbol table for class level variables
		self.__subSymTable = SymbolTable()		# symbol table for subroutine level variables
		self.__className = ""					# need to save the class name for method paramter this
		self.__ifGotoLabelIndex = 0				# index counter for if-goto labels
		self.__whileLabelIndex = 0			# index counter for while labels
		self.compileClass()
			
	def __del__(self):
		print("Closing CompilationEngine...")
		self.__xmlfile.close()
		self.tokenizer = None

	# these rules do not a compile method:
	# type, className, subroutineName, variableName, statement, subroutineCall

	# class grammar 'class' <className> '{' <classVarDec>* <subroutineDec>* '}'
	def compileClass(self):
		getClassNameNext = False 					# boolean variables to control what to expect next in the grammar
		getClassVarDecNext = False
		getSubroutineDecNext = False
		self.writeXML("<class>")					
		self.incTabLevel()
		while (self.tokenizer.hasMoreTokens()):		# begin looping through the .jack file 
			self.tokenizer.advance()				# process next token
			if self.tokenizer.currentToken == "class":
				self.writeXML(self.tokenizer.tokenXML)
				getClassNameNext = True
			elif getClassNameNext:
				self.writeXML(self.tokenizer.tokenXML)
				self.__className = self.tokenizer.currentToken # Save class name for inclusion in symbol table for methods.
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
					getSubroutineDecNext = False
					#print("CompileClass",self.tokenizer.currentToken)
					if self.tokenizer.currentToken == "}":
						self.writeXML(self.tokenizer.tokenXML)
					else:
						self.errorMsg("compileClass", "}", self.tokenizer.currentToken)
		
		self.decTabLevel()
		self.writeXML("</class>")

	#  classVarDec grammar ('static' | 'field') <type> <var-name> (',' <var-name>)* ';'
	def compileClassVarDec(self):
		self.writeXML("<classVarDec>")
		self.incTabLevel()
		
		self.writeXML(self.tokenizer.tokenXML)	# field or static
		symKind = self.tokenizer.currentToken
		self.tokenizer.advance()

		self.writeXML(self.tokenizer.tokenXML) # <type>
		symType = self.tokenizer.currentToken
		self.tokenizer.advance()

		self.writeXML(self.tokenizer.tokenXML) # <varname>
		symName = self.tokenizer.currentToken
		self.__clsSymTable.define(symName, symType, symKind)
		self.incTabLevel()
		self.writeSymTableXML(symName, self.__clsSymTable)
		self.decTabLevel()

		self.tokenizer.advance()

		while (self.tokenizer.currentToken == ","):
			self.tokenizer.advance()
			self.writeXML(self.tokenizer.tokenXML) # <varname>
			symName = self.tokenizer.currentToken
			self.__clsSymTable.define(symName, symType, symKind)
			self.incTabLevel()
			self.writeSymTableXML(symName, self.__clsSymTable)
			self.decTabLevel()
			self.tokenizer.advance()
			
		self.decTabLevel()
		self.writeXML("</classVarDec>")
		return

	# ('constructor' | 'function' | 'method') ('void' | <type>) <subroutine-name> '(' <parameter-list> ')' <subroutine-body>
	def compileSubroutineDec(self):
		getSubroutineTypeNext = True
		getSubroutineNameNext = False
		getOpeningParenNext = False
		#getClosingParenNext = False
		getSubroutineBodyNext = False
		self.writeXML("<subroutineDec>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)		# ('constructor' | 'function' | 'method')
		subroutineType = self.tokenizer.currentToken	# save the type so that it can be passed to Parameter List, methods require special handling
		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			if getSubroutineTypeNext:
				self.writeXML(self.tokenizer.tokenXML)
				getSubroutineTypeNext = False
				getSubroutineNameNext = True

			elif getSubroutineNameNext:
				self.writeXML(self.tokenizer.tokenXML)
				subroutineName = self.tokenizer.currentToken
				print("subroutineName:" , subroutineName)
				getSubroutineNameNext = False
				getOpeningParenNext = True
				self.__subSymTable.startSubroutine()		# start with a clean symbol table

			elif getOpeningParenNext:
				if self.tokenizer.currentToken == "(":
					self.writeXML(self.tokenizer.tokenXML)
					self.compileParameterList(subroutineType)
					self.writeXML(self.tokenizer.tokenXML) # ")"
					getSubroutineBodyNext = True
					getOpeningParenNext = False
				else:
					self.errorMsg("compileSubroutineDec", "(", self.tokenizer.currentToken)
				
			#elif getClosingParenNext:
			#	if self.tokenizer.currentToken == ")":
			#		self.writeXML(self.tokenizer.tokenXML)
			#		getClosingParenNext = False
			#		getSubroutineBodyNext = True
			#	else:
			#		self.errorMsg("compileSubroutineDec", ")", self.tokenizer.currentToken)
				
			elif getSubroutineBodyNext:
				self.compileSubroutineBody(subroutineName)
				getSubroutineBodyNext = False
				break

		self.decTabLevel()
		self.writeXML("</subroutineDec>")
		return

	# Parameter List Grammar ( <type> <var-name> (',' <type> <var-name>)* )?
	def compileParameterList(self, subroutineType):
		self.writeXML("<parameterList>")
		self.incTabLevel()

		symKind = "argument"

		if (subroutineType == "method"):
			symName = "this"
			symType = self.__className
			self.__subSymTable.define(symName, symType, symKind)
			self.incTabLevel()
			self.writeSymTableXML(symName, self.__subSymTable)
			self.decTabLevel()

		self.tokenizer.advance()

		if (self.tokenizer.currentToken != ")"):
			self.writeXML(self.tokenizer.tokenXML) # <type>
			symType = self.tokenizer.currentToken
			self.tokenizer.advance()

			self.writeXML(self.tokenizer.tokenXML) # <varname>
			symName = self.tokenizer.currentToken
			self.__subSymTable.define(symName, symType, symKind)
			print("parameterList",symName, symType, symKind)
			self.incTabLevel()
			self.writeSymTableXML(symName, self.__subSymTable)
			self.decTabLevel()

			self.tokenizer.advance()

			while (self.tokenizer.currentToken == ","):

				self.tokenizer.advance()
				self.writeXML(self.tokenizer.tokenXML) # <type> 
				symType = self.tokenizer.currentToken

				self.tokenizer.advance()
				self.writeXML(self.tokenizer.tokenXML) # <var-name>
				symName = self.tokenizer.currentToken

				self.__subSymTable.define(symName, symType, symKind)
				print("parameterList",symName, symType, symKind)
				self.incTabLevel()
				self.writeSymTableXML(symName, self.__subSymTable)
				self.decTabLevel()

				self.tokenizer.advance()


		#self.writeXML(self.tokenizer.tokenXML)	
		#while (self.tokenizer.hasMoreTokens()):	
		#	if self.tokenizer.nextToken == ")":
		#		break	
		#	self.tokenizer.advance()
		#	self.writeXML(self.tokenizer.tokenXML)
			
		self.decTabLevel()
		self.writeXML("</parameterList>")
		return

	# subroutine Body Grammar; <subroutine-body> '{' <var-dec>* <statements> '}'
	def compileSubroutineBody(self, subroutineName):
		self.writeXML("<subroutineBody>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)		# {

		
		nLocals = 0									# initialize to 0, if this is a void function then it won't change.

		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			#print("compileSubroutineBody", self.tokenizer.nextToken)
			if self.tokenizer.currentToken == "var":
				#self.tokenizer.advance()
				self.compileVarDec()
				
				nLocals = self.__subSymTable.VarCount("local")		# get the count of local variables
				
			else:
				# we are now know all the local vars and can write the vm code for the function
				self.vmWriter.writeFunction(self.__className, subroutineName, nLocals)

				self.compileStatements()
				#print("compileSubroutineBody", self.tokenizer.currentToken)
				self.writeXML(self.tokenizer.tokenXML) # }
				break

		self.decTabLevel()
		self.writeXML("</subroutineBody>")
		return

	# Var Dec Grammar; 'var' <type> <var-name> (',' <var-name>)* ';'
	def compileVarDec(self):
		self.writeXML("<varDec>")
		self.incTabLevel()

		self.writeXML(self.tokenizer.tokenXML)	# var

		symKind = "local"
		self.tokenizer.advance()

		self.writeXML(self.tokenizer.tokenXML) # <type>
		symType = self.tokenizer.currentToken
		self.tokenizer.advance()

		self.writeXML(self.tokenizer.tokenXML) # <varname>
		symName = self.tokenizer.currentToken

		print('var ', symName, symType, symKind)

		self.__subSymTable.define(symName, symType, symKind)
		self.incTabLevel()
		self.writeSymTableXML(symName, self.__subSymTable)
		self.decTabLevel()

		self.tokenizer.advance()

		while (self.tokenizer.currentToken == ","):
			self.tokenizer.advance()
			self.writeXML(self.tokenizer.tokenXML) # <varname>
			symName = self.tokenizer.currentToken
			self.__subSymTable.define(symName, symType, symKind)
			self.incTabLevel()
			self.writeSymTableXML(symName, self.__subSymTable)
			self.decTabLevel()
			self.tokenizer.advance()

		self.decTabLevel()
		self.writeXML("</varDec>")

	# statement Grammar: (<let-statement> | <if-statement> | <while-statement> | <do-statement> | <return-statement>)*
	def compileStatements(self):
		self.writeXML("<statements>")
		self.incTabLevel()
		#self.writeXML(self.tokenizer.tokenXML)
		initialStatement = True
		compiledIf = False
		while (self.tokenizer.hasMoreTokens()):	
			if not initialStatement and not compiledIf: # because we need to check for an else statement in if, we don't need to advance here
				self.tokenizer.advance()	# don't advance on first statement
			compiledIf = False
			initialStatement = False
			if self.tokenizer.currentToken == "let":
				self.compileLet()
			elif self.tokenizer.currentToken == "if":
				self.compileIf()
				compiledIf = True
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
		getEqualSignNext = False
		getSemicolonNext = False

		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			if getVarNameNext:
				#print("varName", self.tokenizer.currentToken)
				self.writeXML(self.tokenizer.tokenXML)
				getVarNameNext = False
				if self.tokenizer.nextToken == '[':
					getVarExpressionNext = True
				else:
					varKind, varIdx = self.convertVarToSymbol(self.tokenizer.currentToken)	# gets the appropriate symbol table variable reference
					print(varKind, varIdx)
					getEqualSignNext = True
			elif getVarExpressionNext:
				self.writeXML(self.tokenizer.tokenXML) # [
				self.compileExpression()
				self.vmWriter.writePop(varKind, varIdx)		# pop the value of the expresssion
				self.tokenizer.advance()
				self.writeXML(self.tokenizer.tokenXML) # ]  not working as intended.
				getEqualSignNext = True
				getVarExpressionNext = False
				
			elif getEqualSignNext:
				if self.tokenizer.currentToken == "=":
					self.writeXML(self.tokenizer.tokenXML)
					getEqualSignNext = False
					self.compileExpression()
					self.vmWriter.writePop(varKind, varIdx)
					getSemicolonNext = True
				else:
					self.errorMsg("compileLet", "=", self.tokenizer.currentToken)

			elif getSemicolonNext:
				if self.tokenizer.currentToken == ";":
					self.writeXML(self.tokenizer.tokenXML)
					break
				else:
					self.errorMsg("compileLet", ";", self.tokenizer.currentToken)
		
		self.decTabLevel()
		self.writeXML("</letStatement>")

# <if-statement>      
#      ::=  'if' '(' <expression> ')' '{' <statements> '}' ( 'else' '{' <statements> '}' )?
#      vm implementation:
#	   compiled (expression)
#		not
#		if-goto L1
#		compiled (statements1)
#		goto L2
#		label L1
#		compiled (statements2)
#		label L2

	def compileIf(self):
		self.writeXML("<ifStatement>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)	 # if

		getOpeningParenNext = True
		getClosingParenNext = False
		getOpeningCurlyBraceNext = False
		doElseStatement = False 				# if True, then processing an else statement

		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			if getOpeningParenNext:
				if self.tokenizer.currentToken == "(":
					self.writeXML(self.tokenizer.tokenXML)
					self.compileExpression()
					getOpeningParenNext = False
					getClosingParenNext = True
				else:
					self.errorMsg("compileIf", '(', self.tokenizer.currentToken)
			elif getClosingParenNext:
				if self.tokenizer.currentToken == ")":
					self.writeXML(self.tokenizer.tokenXML)
					self.vmWriter.writeUnaryOp("~")			# not
					L1 = self.getIfGotoLabel()
					L2 = self.getIfGotoLabel()
					self.vmWriter.writeIf(L1)				# if-goto L1
					getClosingParenNext = False
					getOpeningCurlyBraceNext = True
				else:
					self.errorMsg("compileIf", ')', self.tokenizer.currentToken)
			elif getOpeningCurlyBraceNext:
				if self.tokenizer.currentToken == "{":
					self.writeXML(self.tokenizer.tokenXML)
					self.compileStatements()
					if not doElseStatement:
						self.vmWriter.writeGoto(L2)				# goto L2
						self.vmWriter.writeLabel(L1)			# label L1
					else:
						self.vmWriter.writeLabel(L2)
					self.writeXML(self.tokenizer.tokenXML) # }
					
					if self.tokenizer.hasMoreTokens():
						self.tokenizer.advance()
						if self.tokenizer.currentToken == "else":    
							self.writeXML(self.tokenizer.tokenXML)  #else
							
							doElseStatement = True
							getOpeningCurlyBraceNext = True
						else:
							#self.vmWriter.writeLabel(L2)	# to hand the case where there is no else statement
							break
					else:
						break
				
				else:
					self.errorMsg("compileIf", '{', self.tokenizer.currentToken)
					break
				
		self.decTabLevel()
		self.writeXML("</ifStatement>")

	# while grammar:  'while' '(' <expression> ')' '{' <statements> '}'  
	# vm implementation
# 		label L1
# 		compiled (expression)
# 		not
# 		if-goto L2
# 		compiled (statements)
# 		goto L1
# 		label L2

	def compileWhile(self):
		self.writeXML("<whileStatement>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)	 # while
		L1 = self.getWhileLabel()
		L2 = self.getWhileLabel()
		self.vmWriter.writeLabel(L1)

		getOpeningParenNext = True
		getClosingParenNext = False
		getOpeningCurlyBraceNext = False

		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			if getOpeningParenNext:
				if self.tokenizer.currentToken == "(":
					self.writeXML(self.tokenizer.tokenXML)
					self.compileExpression()
					self.vmWriter.writeUnaryOp("~")		# 		not
					self.vmWriter.writeIf(L2)			# 		if-goto L2
					getOpeningParenNext = False
					getClosingParenNext = True
				else:
					self.errorMsg("compileIf", '(', self.tokenizer.currentToken)
			elif getClosingParenNext:
				if self.tokenizer.currentToken == ")":
					self.writeXML(self.tokenizer.tokenXML)
					getClosingParenNext = False
					getOpeningCurlyBraceNext = True
				else:
					self.errorMsg("compileIf", ')', self.tokenizer.currentToken)
			elif getOpeningCurlyBraceNext:
				if self.tokenizer.currentToken == "{":
					self.writeXML(self.tokenizer.tokenXML)
					self.compileStatements()
					self.vmWriter.writeGoto(L1)			# 		goto L1
					self.writeXML(self.tokenizer.tokenXML) # }
					self.vmWriter.writeLabel(L2)		# 		label L2
					
				
				else:
					self.errorMsg("compileWhile", '{', self.tokenizer.currentToken)
				break

		self.decTabLevel()
		self.writeXML("</whileStatement>")

	# do Grammar  'do' <subroutine-call> ';'
	def compileDo(self):
		self.writeXML("<doStatement>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)	 # do

		doWhile = True
		subroutineName = ""

		while (doWhile):		
			self.tokenizer.advance()
			
			if self.tokenizer.currentToken == "(":
				nArgs = self.compileExpressionList()
				self.vmWriter.writeCall(subroutineName, nArgs)
				self.vmWriter.writePop("temp", 0)				# discard the return value

			elif self.tokenizer.currentToken == ")":
				self.writeXML(self.tokenizer.tokenXML) 
				
			elif self.tokenizer.currentToken == ";":
				self.writeXML(self.tokenizer.tokenXML) 

				doWhile = False

			else:
				self.writeXML(self.tokenizer.tokenXML) 	# subroutine name or className.subroutine name
				subroutineName = subroutineName + self.tokenizer.currentToken

		self.decTabLevel()
		self.writeXML("</doStatement>")
		return

	def compileReturn(self):
		self.writeXML("<returnStatement>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)	 # return

		#while (self.tokenizer.hasMoreTokens()):	
		if self.tokenizer.nextToken != ";":
			self.compileExpression()				# assume return value has been pushed by the expression
		else:
			self.vmWriter.writePush("constant" , 0)	# no return value so push a dummy value

		self.tokenizer.advance()

		if self.tokenizer.currentToken == ";":
			self.writeXML(self.tokenizer.tokenXML)  # ";"
		else:
			self.errorMsg("compileReturn", ';', self.tokenizer.currentToken)
		
		self.vmWriter.writeReturn()

		self.decTabLevel()
		self.writeXML("</returnStatement>")

		return

#<expression>        
#       ::=  <term> (op <term>)*
#<term>              
#       ::=  <int-constant> | <string-constant> | <keyword-constant> | 
#            <var-name> | (<var-name> '[' <expression> ']') | 
#            <subroutine-call> | ( '(' <expression> ')' ) | 
#            (<unary-op> <term>)
#<subroutine-call>   
#       ::=  (<subroutine-name> '(' <expression-list> ')') | ((<class-name> | 
#            <var-name>) '.' <subroutine-name> '(' <expression-list> ')')
#<expression-list>   
#       ::=  (<expression> (',' <expression>)* )?
#<op>                
#       ::=  '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
#<unary-op>          
#       ::=  '-' | '~'
#<keyword-constant>  
#       ::=  'true' | 'false' | 'null' | 'this'

	def compileExpression(self):
		self.writeXML("<expression>")
		self.incTabLevel()
		getFirstTermNext = True
		getOperatorNext = False
		getSecondTermNext = False
		while (self.tokenizer.hasMoreTokens()):		
			
			if getFirstTermNext:
				self.compileTerm()
				getFirstTermNext = False
				if self.tokenizer.nextToken in op:
					getOperatorNext = True
					self.tokenizer.advance()
					operator = self.tokenizer.currentToken
				else:
					break
			elif getOperatorNext:
				self.writeXML(self.tokenizer.tokenXML)
				getOperatorNext = False
				getSecondTermNext = True
			elif getSecondTermNext:
				self.compileTerm()
				self.vmWriter.writeArithmetic(operator)
				break

		self.decTabLevel()
		self.writeXML("</expression>")
		return

	def compileTerm(self):
		self.writeXML("<term>")
		self.incTabLevel()
		while (self.tokenizer.hasMoreTokens()):	

			self.tokenizer.advance()

			if self.tokenizer.tokenType in [C_KEYWORD, C_LITERAL_STRING, C_INTEGER]:
				self.writeXML(self.tokenizer.tokenXML) 
				if self.tokenizer.tokenType == C_INTEGER:
					self.vmWriter.writePush("constant", self.tokenizer.currentToken)	# push constant to the stack

				elif self.tokenizer.tokenType == C_KEYWORD:
					if self.tokenizer.currentToken == "true":							# true
						self.vmWriter.writePush("constant", 0)
						self.vmWriter.writeUnaryOp("~")
					elif self.tokenizer.currentToken == "false":
						self.vmWriter.writePush("constant", 0)							# false

			elif self.tokenizer.currentToken in unaryop:
				self.writeXML(self.tokenizer.tokenXML) 
				unaryOp = self.tokenizer.currentToken
				self.compileTerm()
				self.vmWriter.writeUnaryOp(unaryOp)					# unary operator -  error here

			elif self.tokenizer.currentToken == "(":
				self.writeXML(self.tokenizer.tokenXML) 
				self.compileExpression()
				if self.tokenizer.nextToken == ")":
					self.tokenizer.advance()
					self.writeXML(self.tokenizer.tokenXML) 
				else:
					self.errorMsg("compileTerm:Expression", ")", self.tokenizer.nextToken)

			elif self.tokenizer.tokenType == C_IDENTIFIER:
				if self.tokenizer.nextToken == "[":		# array: (<var-name> '[' <expression> ']')
					self.writeXML(self.tokenizer.tokenXML)  # var-name
					self.tokenizer.advance()
					self.writeXML(self.tokenizer.tokenXML)  # [
					self.compileExpression()
					if self.tokenizer.nextToken == "]":
						self.tokenizer.advance()
						self.writeXML(self.tokenizer.tokenXML) 
					else:
						self.errorMsg("compileTerm:array", "]", self.tokenizer.nextToken)


				elif self.tokenizer.nextToken == "(":	# subroutine call: (<subroutine-name> '(' <expression-list> ')') 
					
					self.writeXML(self.tokenizer.tokenXML)  # subroutine-name
					subroutineName = self.tokenizer.currentToken
					self.tokenizer.advance()
					self.writeXML(self.tokenizer.tokenXML)  # (
					nLocals = self.compileExpressionList()
					self.vmWriter.writeCall(subroutineName, nLocals)		# write subroutine call to vm file
					if self.tokenizer.nextToken == ")":
						self.tokenizer.advance()
						self.writeXML(self.tokenizer.tokenXML) 
					else:
						self.errorMsg("compileTerm:subroutine(expression-list)", ")", self.tokenizer.nextToken)

				elif self.tokenizer.nextToken == ".":	# subroutine call: ((<class-name> | <var-name>) '.' <subroutine-name> '(' <expression-list> ')')
			
					self.writeXML(self.tokenizer.tokenXML)  # (<class-name> | <var-name>)
					subroutineName = self.tokenizer.currentToken
					self.tokenizer.advance()
					self.writeXML(self.tokenizer.tokenXML)  # .
					subroutineName = subroutineName + self.tokenizer.currentToken
					self.tokenizer.advance()
					self.writeXML(self.tokenizer.tokenXML)  # subroutine-name
					subroutineName = subroutineName + self.tokenizer.currentToken
					if self.tokenizer.nextToken == "(":
						self.tokenizer.advance()
						self.writeXML(self.tokenizer.tokenXML)
						nLocals = self.compileExpressionList()
						self.vmWriter.writeCall(subroutineName, nLocals)		# write subroutine call to vm file
						if self.tokenizer.nextToken == ")": 
							self.tokenizer.advance()
							self.writeXML(self.tokenizer.tokenXML)
						else:
							self.errorMsg("compileTerm:class|var-name.subroutine(expression-list)", ")", self.tokenizer.nextToken)
					else:
						self.errorMsg("compileTerm:class|var-name.subroutine(expression-list)", "(", self.tokenizer.nextToken)
			
				else:
					self.writeXML(self.tokenizer.tokenXML)	# variable-name
					varKind, varIdx = self.convertVarToSymbol(self.tokenizer.currentToken)	# push variable in expresssion
					self.vmWriter.writePush(varKind, varIdx)
			break

		self.decTabLevel()
		self.writeXML("</term>")
		return

	def compileExpressionList(self):
		self.writeXML("<expressionList>")
		self.incTabLevel()
		countExpressions = 0

		while (self.tokenizer.hasMoreTokens()):	
			if self.tokenizer.nextToken == ")":
				break
			elif self.tokenizer.nextToken == ",":
				self.tokenizer.advance()
				self.writeXML(self.tokenizer.tokenXML)
				self.compileExpression()
			else:
				self.compileExpression()
			
			countExpressions = countExpressions + 1

		self.decTabLevel()
		self.writeXML("</expressionList>")

		return(countExpressions)

	def errorMsg(self, func, expected, found):
		print("Error in method", func, expected, "was expected", found, "was found.")
		return

	def writeXML(self, s):
		t = "\t" * self.__tabLevel
		self.__xmlfile.writelines(t + s + "\n")
		return

	def writeSymTableXML(self, symName, symTable):
		s = "<symbolName> " + symName + " </symbolName>"
		self.writeXML(s)
		s = "<symbolType> " + symTable.TypeOf(symName) + " </symbolType>"
		self.writeXML(s) 
		s = "<symbolKind> " + symTable.KindOf(symName) + " </symbolKind>"
		self.writeXML(s) 
		s = "<symbolIndex> " + str(symTable.IndexOf(symName)) + " </symbolIndex>"
		self.writeXML(s) 
		return

	def incTabLevel(self):
		self.__tabLevel = self.__tabLevel + 1
		return

	def decTabLevel(self):
		self.__tabLevel = self.__tabLevel - 1
		if self.__tabLevel < 1:
			self.__tabLevel = 1
		return

	def getIfGotoLabel(self):
		s = self.__className + ".IfGotoLabel." + str(self.__ifGotoLabelIndex)
		self.__ifGotoLabelIndex = self.__ifGotoLabelIndex + 1
		return(s)

	def getWhileLabel(self):
		s = self.__className + ".WhileLabel." + str(self.__whileLabelIndex)
		self.__whileLabelIndex = self.__whileLabelIndex + 1
		return(s)

	def convertVarToSymbol(self, varName):
		print(varName)
		# search class symbols
		if self.__clsSymTable.KindOf(varName) != None:
			#print('class')
			if self.__clsSymTable.KindOf(varName) == "static":
				return (self.__clsSymTable.KindOf(varName) , self.__clsSymTable.IndexOf(varName))
			elif self.__clsSymTable.KindOf(varName) == "field":
				return ("this" , self.__clsSymTable.IndexOf(varName))
			else:
				self.errorMsg("convertVarToSymbol", "field or static ", varName + ": " + self.__clsSymTable.KindOf(varName))
				return ("foobar", 0)

		elif self.__subSymTable.KindOf(varName) != None:
			#print('sub')
			return (self.__subSymTable.KindOf(varName) , self.__subSymTable.IndexOf(varName))

		else:
			self.errorMsg("convertVarToSymbol", varName, "nothing")
			return ("foobar", 0)
