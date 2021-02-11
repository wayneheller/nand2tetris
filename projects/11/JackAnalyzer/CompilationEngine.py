# Handles the compilation of tokens from .jack files into xml in the grammar of the Jack language

from JackTokenizer import JackTokenizer
from Constants import *

class CompilationEngine:

	def __init__(self, jackfile):

		self.tokenizer = JackTokenizer(jackfile, True) #initialize the Tokenizer
		xmlFileName = jackfile[:-5] + ".xml"
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
		getOpeningParenNext = False
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
				if self.tokenizer.currentToken == "(":
					self.writeXML(self.tokenizer.tokenXML)
					self.compileParameterList()
					getClosingParenNext = True
					getOpeningParenNext = False
				else:
					self.errorMsg("compileSubroutineDec", "(", self.tokenizer.currentToken)
				
			elif getClosingParenNext:
				if self.tokenizer.currentToken == ")":
					self.writeXML(self.tokenizer.tokenXML)
					getClosingParenNext = False
					getSubroutineBodyNext = True
				else:
					self.errorMsg("compileSubroutineDec", ")", self.tokenizer.currentToken)
				
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
		#self.writeXML(self.tokenizer.tokenXML)	
		while (self.tokenizer.hasMoreTokens()):	
			if self.tokenizer.nextToken == ")":
				break	
			self.tokenizer.advance()
			self.writeXML(self.tokenizer.tokenXML)
			
		self.decTabLevel()
		self.writeXML("</parameterList>")
		return

	# subroutine Body Grammar; <subroutine-body> '{' <var-dec>* <statements> '}'
	def compileSubroutineBody(self):
		self.writeXML("<subroutineBody>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)		# {

		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			#print("compileSubroutineBody", self.tokenizer.nextToken)
			if self.tokenizer.currentToken == "var":
				#self.tokenizer.advance()
				self.compileVarDec()
			else:
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
					getEqualSignNext = True
			elif getVarExpressionNext:
				self.writeXML(self.tokenizer.tokenXML) # [
				self.compileExpression()
				self.tokenizer.advance()
				self.writeXML(self.tokenizer.tokenXML) # ]  not working as intended.
				getEqualSignNext = True
				getVarExpressionNext = False
				
			elif getEqualSignNext:
				if self.tokenizer.currentToken == "=":
					self.writeXML(self.tokenizer.tokenXML)
					getEqualSignNext = False
					self.compileExpression()
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
	def compileIf(self):
		self.writeXML("<ifStatement>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)	 # if

		getOpeningParenNext = True
		getClosingParenNext = False
		getOpeningCurlyBraceNext = False

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
					getClosingParenNext = False
					getOpeningCurlyBraceNext = True
				else:
					self.errorMsg("compileIf", ')', self.tokenizer.currentToken)
			elif getOpeningCurlyBraceNext:
				if self.tokenizer.currentToken == "{":
					self.writeXML(self.tokenizer.tokenXML)
					self.compileStatements()
					self.writeXML(self.tokenizer.tokenXML) # }
					
					if self.tokenizer.hasMoreTokens():
						self.tokenizer.advance()
						if self.tokenizer.currentToken == "else":    
							self.writeXML(self.tokenizer.tokenXML) 
							getOpeningCurlyBraceNext = True
						else:
							break
					else:
						break
				
				else:
					self.errorMsg("compileIf", '{', self.tokenizer.currentToken)
					break
				
		self.decTabLevel()
		self.writeXML("</ifStatement>")

	# while grammar:  'while' '(' <expression> ')' '{' <statements> '}'  
	def compileWhile(self):
		self.writeXML("<whileStatement>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)	 # if

		getOpeningParenNext = True
		getClosingParenNext = False
		getOpeningCurlyBraceNext = False

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
					getClosingParenNext = False
					getOpeningCurlyBraceNext = True
				else:
					self.errorMsg("compileIf", ')', self.tokenizer.currentToken)
			elif getOpeningCurlyBraceNext:
				if self.tokenizer.currentToken == "{":
					self.writeXML(self.tokenizer.tokenXML)
					self.compileStatements()
					self.writeXML(self.tokenizer.tokenXML) # }
					
				
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

		while (self.tokenizer.hasMoreTokens()):		
			self.tokenizer.advance()
			self.writeXML(self.tokenizer.tokenXML)
			if self.tokenizer.currentToken == "(":
				self.compileExpressionList()
				#self.writeXML(self.tokenizer.tokenXML) # closing paren
			if self.tokenizer.currentToken == ";":
				break

		self.decTabLevel()
		self.writeXML("</doStatement>")
		return

	def compileReturn(self):
		self.writeXML("<returnStatement>")
		self.incTabLevel()
		self.writeXML(self.tokenizer.tokenXML)	 # return

		while (self.tokenizer.hasMoreTokens()):	
			if self.tokenizer.nextToken == ";":
				self.tokenizer.advance()
				self.writeXML(self.tokenizer.tokenXML)
				break	
			else:
				self.compileExpression()
		
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
				else:
					break
			elif getOperatorNext:
				self.writeXML(self.tokenizer.tokenXML)
				getOperatorNext = False
				getSecondTermNext = True
			elif getSecondTermNext:
				self.compileTerm()
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
			elif self.tokenizer.currentToken in unaryop:
				self.writeXML(self.tokenizer.tokenXML) 
				self.compileTerm()
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
					self.tokenizer.advance()
					self.writeXML(self.tokenizer.tokenXML)  # (
					self.compileExpressionList()
					if self.tokenizer.nextToken == ")":
						self.tokenizer.advance()
						self.writeXML(self.tokenizer.tokenXML) 
					else:
						self.errorMsg("compileTerm:subroutine(expression-list)", ")", self.tokenizer.nextToken)

				elif self.tokenizer.nextToken == ".":	# subroutine call: ((<class-name> | <var-name>) '.' <subroutine-name> '(' <expression-list> ')')
			
					self.writeXML(self.tokenizer.tokenXML)  # (<class-name> | <var-name>)
					self.tokenizer.advance()
					self.writeXML(self.tokenizer.tokenXML)  # .
					self.tokenizer.advance()
					self.writeXML(self.tokenizer.tokenXML)  # subroutine-name
					if self.tokenizer.nextToken == "(":
						self.tokenizer.advance()
						self.writeXML(self.tokenizer.tokenXML)
						self.compileExpressionList()
						if self.tokenizer.nextToken == ")": 
							self.tokenizer.advance()
							self.writeXML(self.tokenizer.tokenXML)
						else:
							self.errorMsg("compileTerm:class|var-name.subroutine(expression-list)", ")", self.tokenizer.nextToken)
					else:
						self.errorMsg("compileTerm:class|var-name.subroutine(expression-list)", "(", self.tokenizer.nextToken)
			
				else:
					self.writeXML(self.tokenizer.tokenXML)	# variable-name
			break

		self.decTabLevel()
		self.writeXML("</term>")

	def compileExpressionList(self):
		self.writeXML("<expressionList>")
		self.incTabLevel()
		while (self.tokenizer.hasMoreTokens()):	
			if self.tokenizer.nextToken == ")":
				break
			elif self.tokenizer.nextToken == ",":
				self.tokenizer.advance()
				self.writeXML(self.tokenizer.tokenXML)
				self.compileExpression()
			else:
				self.compileExpression()
			

		self.decTabLevel()
		self.writeXML("</expressionList>")

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