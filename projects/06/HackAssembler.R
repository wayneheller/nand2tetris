# Hack Assembler - Nand2Tetris
# December 31, 2020
# To convert Hack Assembly Language programs into Hack Machine Language
# Assembly programs are read from Text files xxx.asm and text language files are
# Output to xxx.hack
# File names and paths must be updated in the code prior to execution

library(collections) # using this library for the Dictionary functionality


ASMfile <- file.path('.', 'pong', 'PongL.asm')
HACKfile <- file.path('.', 'pong', 'PongL.hack')

# Load standard symbols into a dictionary
symDict <- dict()
symDict$set("R0", 0)$set("R1",1)$set("R2",2)$set("R3",3)$set("R4",4)
symDict$set("R5", 5)$set("R6",6)$set("R7",7)$set("R8",8)$set("R9",9)
symDict$set("R10", 10)$set("R11",11)$set("R12",12)$set("R13",13)$set("R14",14)$set("R15",15)
symDict$set("SCREEN", 16384)$set("KBD", "24576")
symDict$set("SP", 0)$set("LCL", "1")$set("ARG", "2")$set("THIS", "3")$set("THAT", "4")

# Load jump command bits j1 j2 j3 and their mapping into a distinct dictionary
jumpDict <- dict()
jumpDict$set("null", "000")$set("JGT","001")$set("JEQ","010")$set("JGE","011")
jumpDict$set("JLT", "100")$set("JNE","101")$set("JLE","110")$set("JMP","111")

# Load destination command bits d1 d2 d3 and their mapping into distinct dictionary
destDict <- dict()
destDict$set("null", "000")$set("M","001")$set("D","010")$set("MD","011")
destDict$set("A", "100")$set("AM","101")$set("AD","110")$set("AMD","111")

# Load comparison command bits c1-c6 as well as the 'a' bit into a distinct dictionary
compDict <- dict()
compDict$set("0",   "0101010")
compDict$set("1",   "0111111")
compDict$set("-1",  "0111010")
compDict$set("D",   "0001100")
compDict$set("A",   "0110000")$set("M",   "1110000")
compDict$set("!D",  "0001101")
compDict$set("!A",  "0110001")$set("!M",  "1110001")
compDict$set("-D",  "0001111")
compDict$set("-A",  "0110011")$set("-M",  "1110011")
compDict$set("D+1", "0011111")
compDict$set("A+1", "0110111")$set("M+1", "1110111")
compDict$set("D-1", "0001110")
compDict$set("A-1", "0110010")$set("M-1", "1110010")
compDict$set("D+A", "0000010")$set("D+M", "1000010")
compDict$set("D-A", "0010011")$set("D-M", "1010011")
compDict$set("A-D", "0000111")$set("M-D", "1000111")
compDict$set("D&A", "0000000")$set("D&M", "1000000")
compDict$set("D|A", "0010101")$set("D|M", "1010101")

nextavailmemloc <- 16 # first available memory location for named variables.  16 is hardware specific value

# Primary interface to the conversion program
# Inputs are the paths to the .asm file to translate and the output .hack file
# The program executes in 2 passes through the .asm file
# First pass loads the symbol dictionary with program control labels, e.g. (GOTO_THIS_LOCATION)
# During the first pass, a program instruction counter is maintained so that its value can be loaded
# into the symbol dictionary for reference in pass 2.  For example if (GOTO_THIS_LOCATION) is a reference
# to instruction 15 in the code, then a key pair GOTO_THIS_LOCATION, 15 is stored.
# During pass 2, instructions are coded using the symbol, comp, dest, jump dictionaries
# and the output file is created, appending 1 instruction at a time.
Main <- function(filepath2ASM, filepath2HACK){
    
    
    # will establish instruction counter and program line counter at 0
    indcurrentinstr <- 0 # index of current instruction
    
    for (pass in 1:2) { # pass 1 is to set labels and variables, pass 2 is to code instructions
        conASM = file(filepath2ASM, "r") # open a read only connection to the asm file for both passes
        if (pass == 2) {conHACK = file(filepath2HACK, "w")} # open the output file for pass 2 only
        # Begin reading the .asm file from start to finish
        while ( TRUE ) {
            line <- readLines(conASM, n = 1) # reads the next line
            if ( length(line) == 0 ) {
                break                        # breaks at end of the file
            }
            x <- cleanASMInstructionLine(line) # remove whitespace and comments
            print(x[1])
            if (!is.na(x) && x != '') {        # if x is NA or empty string, then this is an empty line or comment line
                if (substring(x,1,1) != "(") { # if this line is not a label, e.g. (GOTO_THIS_LOCATION), then is a valid instruction
                    print(paste("valid instruction:",indcurrentinstr)) 
                    x <- parseInstruction(x)   # parse the instruction into components
                                               # the parsed instruction will be returned in two ways; 
                                               # for A instruction:
                                               #    x$opcode = 'A'
                                               #    x$address = a string of numeric (decimal), e.g. @12 is the instruction, then address will contain '12'
                                               #    x$symbol = a string for a lable reference, e.g. @GOTO_THIS_LOCATION, then address will contain 'GOTO_THIS_LOCATION'
                                               # for C instruction: 
                                               #    x$opcode = 'C'
                                               #    x$dest, x$comp, x$jump will contain the applicable parts
                                               #    dest = comp ; jump is the generic format of a C instruction
                                               #    see instruction spec on nand2tetris.org for more info
                    if (pass==2) {
                        x <- codeInstruction(x) # will only code the instruction in 2nd pass, using the dictionaries
                                                # to map Assembler instructions to 16-bit hack machine language 
                        print(x)  
                        writeLines(x, conHACK)  # outputs instruction to the .hack file
                    }
                    else {                      # for the first pass, increment the program counter for all valid instructions
                                                # note that comments, blank lines, and program control labels are not valid instructions
                        indcurrentinstr <- indcurrentinstr + 1
                    }
                }
                else { # special handling for labels.  Only valid for pass 1 but did not put the conditional around it
                       # if the label does not have a representation in the symbol dictionary, then it is added
                    print("is a label and not a valid instruction") 
                    # for first pass will add to symbolDict the program location for this label
                    l <- nchar(x)
                    label <- substring(x, 2, l-1) # remove the parentheses from the symbol
                    if (!symDict$has(label)){
                        print(paste("This is the label description:", label, "and it's value", indcurrentinstr))
                        symDict$set(label, indcurrentinstr) # set the label value to the next instruction
                        
                    }
                }
            }
            else {
                print("invalid instruction") # if working correctly, and the .asm file is well-formed should not reach this condition
            }
            
            
    
        }
        
        close(conASM) # close the .asm file after each pass.  no way to reset file position to beginning
        
    } # end for loop for passes
    close(conHACK)    # close the output .hack file
}

# removes the whitespace and comments from a line of instructions
# will return NA when the line is blank
# will return empty string when line is a comment line
cleanASMInstructionLine <- function(ASMline){
    #print(ASMline)
    x <- gsub(" ", "", ASMline, fixed = TRUE)       # remove whitespace
    x <- strsplit(x,"//|[^[:print:]]",fixed=FALSE)  # split out inline comments
    return(x[[1]][1])                               # the first part contains command
                                                    # or character(0) if no command
    }

parseInstruction <- function(ASMLine){
    # return a list object as follows:
    # for A instruction:
    #    x$opcode = 'A'
    #    x$address = a string of numeric (decimal), e.g. @12 is the instruction, then address will contain '12'
    #    x$symbol = a string for a lable reference, e.g. @GOTO_THIS_LOCATION, then address will contain 'GOTO_THIS_LOCATION'
    # for C instruction: 
    #    x$opcode = 'C'
    #    x$dest, x$comp, x$jump will contain the applicable parts
    #    dest = comp ; jump is the generic format of a C instruction
    #    see instruction spec on nand2tetris.org for more info
    
    if (substring(ASMLine, 1, 1)=='@')  { # all 'A' instructions begin with @
        OpCode <- 'A'
        s <- substring(ASMLine, 2)              # remove the @ symbol and process remaining
        
        if (!grepl("\\D", s)) {                 # check if remainders has for only numbers
            address <- s                        # if numeric put that value in address  
            symbol <- NA                        # set symbol to NA
        }
        else {
            address <- NA
            symbol <- s                         # if the remainder is not numeric, it is a reference to a label
        }
            
        r <- list(OpCode, address, symbol )
        names(r) <- c('opcode', 'address', 'symbol')
        return(r)
    }
    else {
        OpCode <- 'C'
        s <- ASMLine
        if (grepl(";",s, fixed = TRUE)) {       # if string contains semicolon, then it is a comp;jump instruction
            x <- strsplit(s,";|[^[:print:]]",fixed=FALSE)
            comp <- x[[1]][1]
            jump <- x[[1]][2]
            dest <- "null"
        }
        else {
            if (grepl("=",s, fixed = TRUE)){    # if the string contains an equal sign, then it is a dest=comp instruction
                x <- strsplit(s,"=|[^[:print:]]",fixed=FALSE)
                dest <- x[[1]][1]
                comp <- x[[1]][2]
                jump <- "null"
            }
            else {
                dest <- "null"                  # otherwise is is a comp instruction with no destination
                comp <- s
                jump <- "null"
            }
            
        }
         
        r <- list(OpCode, dest, comp, jump)
        names(r) <- c('opcode', 'dest', 'comp', 'jump')
        return(r)
        }
    
    
}

# map the assembler instructions to 16 bit hack machine language
# input is a list object of the form described in function parseInstruction
# also handles the assignment of new memory locations to user defined variable names
codeInstruction <- function(x) {
    if (x$opcode == 'A') {
        if (!is.na(x$address)) { # convert address to a binary string
            s <- x$address
        }
        else { # lookup symbol
            if (symDict$has(x$symbol)) { # look whether symbol dictionary has an existing key pair, if so return it.
                                         # labels will already have been added to the dictionary in pass 1
                s <- symDict$get(x$symbol)
            }
            else {                       # this condition is reached the first time a named variable is referenced
                print(paste("symbol", x$symbol, "not found adding a new memory location", nextavailmemloc))
                symDict$set(x$symbol,nextavailmemloc) # add a reference to the variable name in the symbol dictionary
                s <- symDict$get(x$symbol)
                nextavailmemloc <<- nextavailmemloc + 1 # advance the global variable to the next memory location.  
                                                        # Note that the <<- assignment operations is needed to reference the parent scope of the variable
                print(paste("next available memory location is:", nextavailmemloc))
            }
        }
        # convert the decimal values to 16-bit binary string
        s <- rev(intToBits(s))
        s <- paste(as.integer(s), collapse = "")
        s <- substring(s, 17) # The native function converts it to 32-bit so need to trim it back to first 16
        return(s)        
    }
    else { # opcode == 'C'
        dest <- destDict$get(x$dest)
        comp <- compDict$get(x$comp)
        jump <- jumpDict$get(x$jump)
        
        return(paste0("111",comp,dest,jump, collapse=NULL)) # pad the most significant bits with 111 per the language spec
    }
}
