/------------------------------------------------------------
/                       INSTRUCTIONS
/------------------------------------------------------------
/
/	|		> Circulate and output program
/	|		------------------------------
/	|		FG1 : print Output
/	|		FG2 : load Input
/	|		FG3 : circulate left
/	|		FG4 : circulate right
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

/------------print output on flag1

	LDF
	NND	10H
	ADD	1
	SAR S2
	SIZ
	RAS
	JMP	
	LDA EFH
	ANF

	LDA>VAL
	OUT

/------------Load input on flag2

S2,	LDF
	NND	20H
	ADD	1
	SAR S3
	SIZ	
	RAS
	JMP	
	LDA DFH
	ANF

	LDI
	STA>VAL
	
/------------circulate left on flag3
	
S3,	LDF
	NND	40H
	ADD	1
	SAR S4
	SIZ	
	RAS
	JMP	
	LDA BFH
	ANF

	LDA>VAL
	CIL
	LDA>VAL
	CIL
	STA>VAL

/------------circulate right on flag4

S4,	LDF
	NND	80H
	ADD	1
	SAR EXT
	SIZ	
	RAS
	JMP	
	LDA 7FH
	ANF

	LDA>VAL
	INV
	CIL
	LDA>VAL
	INV
	CIL
	INV
	STA>VAL

/------------Exit
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