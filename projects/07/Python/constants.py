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

switcher = {
	"add": C_ARITHEMETIC,
	"sub": C_ARITHEMETIC,
	"pop": C_POP,
	"push": C_PUSH,
	"label": C_LABEL,
	"if": C_IF,
}

switcherSegment = {
	"constant": "constant",
	"local": "LCL",
	"argument": "ARG",
	"this": "THIS",
	"that": "THAT",
	"temp": "5",
	"static": "static"
	}