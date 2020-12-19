# nand2tetris
Completed Project files for Nand2Tetris.org 
Tips for completing the projects:

Chapter 1: I found it helpful to create an Excel workbook of truth tables for each of the basic chips.  As I was building a new chip, I would reference the prior ones to see how they could be manipulated to provide the necessary output.  There is a copy of my Excel file with notes at the root of the project folder in this repo.

Chapter 2: Building the ALU
There are a couple of learning unlocks that I discovered on the way that allowed me to greatly simplify the code and build the ALU without helper chips and only using the built-in chips from Chapters 1 and 2.
* When considering how to provide conditional (if/then) functionality, take a hard look at the Multiplexor chip Mux.  
* When implementing the ng and zr output signals, you may want to create a subbus from an internal pin.  Subbussing internal pins is not supported by the Hardware Simulator.  To work around this limitation, I initial built some helper chips and was able to successfully complete the assignment, knowing that approach was not recommended by the instructors.  The missing piece of information is documented in the Survival Guide but I didn't grok it right away.  it is possible to create mutiple outputs from a chip.  For example, And16 (a=a, b=b, out=out, out[15]=t1, out[0..7]=tlsb, out[8...15]= tmsb, and so on).  With this bit of knowledge, you should be able to create all the additional logic necessary for the ng and zr signal outputs.
