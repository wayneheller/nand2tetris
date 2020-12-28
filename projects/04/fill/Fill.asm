// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
@8191
D=A
@n // number of words of data on the screen
M=D

@16384
D=A
@base // base address of the Screen memory
M=D 

@color // the color to paint the screen 0=white, -1=black
M=0

@24576
D=A
@keyboard
M=D

(BEGIN)
// initialize loop counter i
@i
M=0

@base
D=M
@wordtofill // the location on the screen to fill
M=D

// Test Whether Any Key is Press
@keyboard
A=M
D=M
@NOT_PRESSED
D;JEQ

// Set the color to black because a key is pressed
@color
M=-1
@LOOP
0;JMP

(NOT_PRESSED)
@color
M=0

(LOOP)
@i
D=M
@n
D=D-M
@BEGIN
D;JGT // if i > n then go to the beginning

// calcuate the screen address of the word to be set
@i
D=M
@base
D=D+M
@wordtofill
M=D
@color
D=M
@wordtofill
A=M
M=D

//increment i++
@i
D=M+1
M=D

@LOOP
0;JMP

