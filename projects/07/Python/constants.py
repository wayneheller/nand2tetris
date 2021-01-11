# shared constants and globals across modules
# constants.py

C_ARITHEMETIC = 1
C_POP = 2
C_PUSH = 3
C_LABEL = 4
C_GOTO = 5
C_IF = 6
C_FUNCTION = 7
C_RETURN = 8
C_CALL = 9

switcherCmdType = {
	"add": C_ARITHEMETIC,
	"sub": C_ARITHEMETIC,
	"eq":  C_ARITHEMETIC,
	"lt":  C_ARITHEMETIC,
	"gt":  C_ARITHEMETIC,
	"and": C_ARITHEMETIC,
	"or":  C_ARITHEMETIC,
	"neg": C_ARITHEMETIC,
	"not": C_ARITHEMETIC,
	"pop": 		C_POP,
	"push": 	C_PUSH,
	"label":	C_LABEL,
	"goto": 	C_GOTO,
	"if-goto":  C_IF,
	"function": C_FUNCTION,
	"call": 	C_CALL,
	"return": 	C_RETURN

}

switcherSegment = {
	"constant": "constant",
	"local": "LCL",
	"argument": "ARG",
	"this": "THIS",
	"that": "THAT",
	"temp": "5",
	"static": "static",
	"pointer": "pointer"
	}

switcherCondition = {
	"eq": "JEQ",
	"lt": "JLT",
	"gt": "JGT"

}