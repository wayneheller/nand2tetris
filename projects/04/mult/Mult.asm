// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.
// Approach is to Add R0 R1 time

// for (i=1; i < n; i++) where n = R1 { 
//    sum = sum + R0
// }

// initialize variables
// n = R1
@R1
D=M
@n
M=D
// sum = 0
@sum
M=0
// i=1
@i
M=1

(LOOP) // Beginning of the add loop
@i
D=M
@n
D=D-M
@STOP
D;JGT // End the loop if i > n

@R0
D=M
@sum
D=D+M // add R0 to the sum
@sum
M=D

@i // increment i++
M=M+1

@LOOP // repeat the LOOP
0;JMP


(STOP)
// Set R2 = sum
@sum
D=M
@R2
M = D

// End with Infinite Loop
(END)
@END
0; JMP

