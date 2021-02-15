# Constants for JackAnalyzer

C_KEYWORD = 1
C_SYMBOL = 2
C_INTEGER = 3
C_LITERAL_STRING = 4
C_IDENTIFIER = 5


keywords = ['class' , 'constructor' , 'function' , 'method' ,   'field' , 'static' , 'var' , 'int' , 'char' , 'boolean' , 'void' , 'true' , 'false' , 'null' , 'this' , 'let' , 'do' , 'if' , 'else' , 'while' , 'return']

symbols = ['{' , '}' , '(' , ')' , '[' , ']' , '.' , ',' , ';' ,  '+' , '-' , '*' , '/' , '&' , '|' , '<' , '>' , '=' , '~', '/**']

op = ['+' , '-' , '*' , '/' , '&' , '|' , '<' , '>' , '=']

switcherOp = {
	"+" : "add",
	"-" : 'sub',
	"&" : "and",
	"|" : "or",
	"<" : "lt",
	">" : "gt",
	"=" : "eq"
}

switcherUnaryOp = {
	"~" : "not",
	'-' : "neg"
}

unaryop = [ '~', '-']

switcherSymbol = {
	">" : "&gt;",
	"<" : "&lt;",
	'"' : "&quot;",
	"&" : "&amp;"
}

classVarDec = ['static', 'field']

subroutineDec = ['constructor', 'function', 'method']