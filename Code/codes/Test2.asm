/------------------------------------------------------------
/                       INSTRUCTIONS
/------------------------------------------------------------
/
/	|		> Calculator program
/	|		------------------------------
/	|		FG1 : Load Input
/	|		FG2 : Add Input
/	|		FG3 : Subtract Input
/	|		FG4 : Multiply Input
/	|___________________________________________
/
/------------------------------------------------------------
/                        IO PROGRAM
/------------------------------------------------------------

	RAS		/skip address
RTI,0
	STA>TAC
	LDA>RTI /check if start
	SAR RUN
	SIZ
	RAS
	JMP		/jump to main program if no address is present

/------------[ Check flag 1 ]----------\

	LDF
	NND	10H
	ADD	1
	SAR S2
	SIZ
	RAS
	JMP	
	LDA EFH
	ANF
/- - - - - - - Load Input - - - - - - -\

	LDI
	STA>VAL

/------------[ Check flag 2 ]----------\

S2,	LDF
	NND	20H
	ADD	1
	SAR S3
	SIZ	
	RAS
	JMP	
	LDA DFH
	ANF
/- - - - - - - Add Input - - - - - - -\

	LDI
	ADD>VAL
	STA
	
/------------[ Check flag 3 ]----------\
	
S3,	LDF
	NND	40H
	ADD	1
	SAR S4
	SIZ	
	RAS
	JMP	
	LDA BFH
	ANF
/- - - - - - Subtract Input - - - - - -\

	LDI
	STA>TM1
	NND
	ADD 1
	ADD>VAL
	STA

/------------[ Check flag 4 ]----------\

S4,	LDF
	NND	80H
	ADD	1
	SAR EXT
	SIZ	
	RAS
	JMP	
	LDA 7FH
	ANF

/- - - - - - Multiply Input - - - - - -\

	LDI		/setup memory
	STA>TM1
	LDA>VAL
	STA>TM2
	LDA 0
	STA>VAL
	LDA -8
	STA>TM3

LP1,LDA>TM1
	NND 1
	ADD 1
	SAR LC1
	SIZ
	RAS
	JMP
	LDA>TM2
	ADD>VAL
	STA
LC1,LDA>TM1
	INV
	CIL
	INV
	STA
	LDA FBH
	ANF
	LDA>TM2
	CIL
	STA
	LDA>TM3
	ADD 1
	STA
	SAR LP1
	SIZ
	JMP


/------------[    EXIT    ]-----------\
EXT,LDA>TAC
	SAR>RTI
	JMP

/------------------------------------------------------------
/                           MAIN
/------------------------------------------------------------

RUN,LDA 2H
	XRF		/set interrupt enabled on
	XRF		/set interrupt enabled off
	JMP>RUN


/------------------------------------------------------------
/                           DATA
/------------------------------------------------------------

	ORG 400
TAC,0H
VAL,0H
TM1,0H
TM2,0H
TM3,0H