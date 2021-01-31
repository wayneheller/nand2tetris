# Handles the tokenization of .jack files into xml for compilation

# import re
# text = "python is, an easy;language; to, learn."
# separators = "; ", ", "


#def custom_split(sepr_list, str_to_split):
#    # create regular expression dynamically
#    regular_exp = '|'.join(map(re.escape, sepr_list))
#    return re.split(regular_exp, str_to_split)



from Constants import *

class JackTokenizer:

	def __init__(self, jackfile, emitXML):
		self.__jackfile = open(jackfile, 'r')
		self.__currentToken = None
		self.__nextTokens = []
		self._resetProperties
		self.__emitXML = emitXML

		if emitXML:
			xmlFileName = jackfile[:-5] + "T_.xml"
			self.__xmlfile = open(xmlFileName, 'w')
			self.__xmlfile.writelines("<tokens>\n")

		
	def __del__(self):
		self.__jackfile.close()
		if self.__emitXML:
			self.__xmlfile.writelines("</tokens>\n")
			self.__xmlfile.close()

	def advance(self):
		#print(self.__nextTokens)
		self.__currentToken = self.__nextTokens.pop(0)	# set the new current token from the list of next tokens
		#print(self.__currentToken)
		self._resetProperties()						# sets the current properties to None
		self._tokenType = self.__currentToken		# sets the  properties for the current token
		if self.__emitXML:
			self._writeXML()


	def _writeXML(self):
		if self.tokenType == C_KEYWORD:
			self.__xmlfile.writelines("<keyword> " + self._keyword + " </keyword>\n")
			return
		if self.tokenType == C_SYMBOL:
			self.__xmlfile.writelines("<symbol> " + self._escapeSymbol(self._symbol) + " </symbol>\n")
			return	
		if self.tokenType == C_LITERAL_STRING:
			self.__xmlfile.writelines("<stringConstant> " + self._stringVal + " </stringConstant>\n")
			return
		if self.tokenType == C_INTEGER:
			self.__xmlfile.writelines("<integerConstant> " + self._intVal + " </integerConstant>\n")
			return
		if self.tokenType == C_IDENTIFIER:
			self.__xmlfile.writelines("<identifier> " + self._identifier + " </identifier>\n")
			return	
	
	# Get the escape code for the xml file if one exists, else return the symbol
	def _escapeSymbol(self, sym):
		 return(switcherSymbol.get(sym, sym))
		 


	def hasMoreTokens(self):

		
		if len(self.__nextTokens) > 0:			# there are more tokens on the current line of Jack code to process
			return(True)

		s = self.__jackfile.readline()
		if (s == ''):							# test whether the end of line -- an empty string -- has been reached, 
			return(False)
		
		elif (s == '\n'):						# test whether new line is \n which is blank
			self.hasMoreTokens()
			return(True)

		else:
			self._parseNextLine(s)
			if len(self.__nextTokens) == 0:
				print("Calling hasMoreTokens recursively for full line comment")
				return(self.hasMoreTokens())		# if we've hit a full line comment, need to call recursively
			else:
				return(True)


	def _parseNextLine(self, s):
		
		# remove leading and trailing whitespace
		s = s.strip()

		# split the line on spaces
		#s = s.split()

		token = ""
		i = 0
		while i < len(s):

			if s[i] != " ":
				token = token + s[i]
			
				if token in keywords:					# is the token a keyword?  Doesn't handle the case where a keyword is part of an identifier, e.g trueVal
					print("Tokenizing keyword", token)
					self.__nextTokens.append(token)
					token = ""

				elif token in symbols:
					if token != '/':
						print("Tokenizing symbol", token)
						self.__nextTokens.append(token)
						token = ""
					else:
						print("Tokenizing fwd slash /")
						if i < len(s) - 1:		# There are more characters after the slash
							if s[i+1] == '/': 		# The start of an end of line comment
								print("Processing eol comment")
								break
							elif s[i+1:i+3] == '**':		# The start of an inline comment
								print("Processing inline comment, i=", i)
								i = i + s[i:].index("*/") + 2	# find the end of the inline comment and advance to that position /***/
								print("Processing inline comment, new value for i=", i)
								token =""
							else:
								print("Tokenizing division symbol, token")
								self.__nextTokens.append(token) # this is the symbol for division
								token = ""
						else:
							token = ""
							print("Forward slash / at end of line, ERROR")
				elif token.isnumeric():
					if i < len(s) - 1:			# There are more characters on the line
						if not(s[i+1].isnumeric()):		# No more digits left
							print("Tokenizing integer", token)
							self.__nextTokens.append(token) 
							token = ""	
					else:
						token = ""
						print("integer at the end of line, ERROR")
				elif token == '"':					# the beginning of a literal string
					j = i + 1 + s[i+1:].index('"')			# the end of the string
					print("Tokenizing literal", s[i:j+1])
					self.__nextTokens.append(s[i:j+1]) # including quotes that will be stripped out later
					i = j 
					token = ""
				else:								# this is an identifier
					if i < len(s) - 1:			# There are more characters on the line
						if not(s[i+1].isalnum() and not((s[i+1] == "_"))): 
							if not token.strip() == "":
								print("Tokenizing identifier", token)
								self.__nextTokens.append(token) 
							token = ""
					else:
						token = ""
						print("identifier at the end of line, ERROR")
			

			i = i + 1

	def _resetProperties(self):
		self.__tokenType = None
		self.__keyword = None
		self.__symbol = None
		self.__identifier = None
		self.__intVal = None
		self.__stringVal = None
		return



	@property
	def tokenType(self):
		return self.__tokenType

	@tokenType.setter
	def _tokenType(self, token):

		if token in keywords:
			self.__tokenType = C_KEYWORD
			self._keyword = token
			return

		if token in symbols:
			self.__tokenType = C_SYMBOL
			self._symbol = token
			return

		if token.isnumeric():
			self.__tokenType = C_INTEGER
			self._intVal = token
			return

		if token[0] == '"':
			self.__tokenType = C_LITERAL_STRING
			print("The String Val is:", token,"<endtoken>")
			self._stringVal = token[1:-1]		# strip out the quotes from the token
			print("The String Val is:", self._stringVal,"<endtoken>")
			return

		self.__tokenType = C_IDENTIFIER
		self._identifier = token
		return

	@property
	def keyword(self):
		return self.__keyword

	@keyword.setter
	def _keyword(self, s):
		self.__keyword = s

	@property
	def symbol(self):
		return self.__symbol

	@symbol.setter
	def _symbol(self, s):
		self.__symbol = s

	@property
	def identifier(self):
		return self.__identifier

	@identifier.setter
	def _identifier(self, s):
		self.__identifier = s

	@property
	def intVal(self):
		return self.__intVal

	@intVal.setter
	def _intVal(self, n):
		self.__intVal = n

	@property
	def stringVal(self):
		return self.__stringVal

	@stringVal.setter
	def _stringVal(self, s):
		print("Setting stringVal to:", s)
		self.__stringVal = s

		    