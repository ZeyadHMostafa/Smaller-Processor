MEMORY_SIZE = 2**16
INTERRUPT_ADDRESS = 1
def check_bit(a,n):
	return (a&(2**n)) !=0

def word_to_int(word,signed=False):
	return int.from_bytes(word, byteorder='big', signed=signed)

class Processor():
	def __init__(self,rom=None,set_S=False):
		self.reset(rom,set_S)

	def reset(self,rom=None,set_S=False):
		#registers
		self.AR = 0
		self.AC = 0
		self.PC = 0
		self.IR = 0
		self.INPR = 0
		self.OUTR = 0
		#flags
		self.S = False
		self.IEN = False
		self.E = False
		self.B = False
		self.FG1 = False
		self.FG2 = False
		self.FG3 = False
		self.FG4 = False
		#internal
		self.SC = False
		self.R = False
		#Memory
		self.MEM = [0]*MEMORY_SIZE
		if rom:
			try:
				f = open(rom, 'rb')
				bs = f.read()
				for i in range(len(bs)//2):
					self.MEM[i] = word_to_int(bytearray([bs[2*i],bs[2*i+1]]))
			except Exception:
				pass
			
		#External
		self.set_S = set_S
		self.set_FG1 = False
		self.set_FG2 = False
		self.set_FG3 = False
		self.set_FG4 = False

	def cycle(self):
		#handle asynchronus
		##flags
		self.S = self.set_S or self.S
		self.FG1 = self.set_FG1 or self.FG1
		self.FG2 = self.set_FG2 or self.FG2
		self.FG3 = self.set_FG3 or self.FG3
		self.FG4 = self.set_FG4 or self.FG4
		self.set_S = False
		self.set_FG1 = False
		self.set_FG2 = False
		self.set_FG3 = False
		self.set_FG4 = False
		##controls
		IRT = self.IR if self.SC else 0
		ALU_DS = IRT//2**13
		ALU_CS = check_bit(IRT,15)
		FLU_CS = (IRT//2**6)%4
		IR_EN = (not self.SC) and (not self.R)
		OUTR_EN = check_bit(IRT,4)
		AC_EN = self.SC
		PC_CLR = self.R
		PC_EN = check_bit(IRT,2)
		PC_INC = (IR_EN or (check_bit(IRT,3) and (self.AC == 0)) or check_bit(IRT,12))and self.S and (not PC_EN)
		AR_EN = check_bit(IRT,0)
		AB1 = self.R
		AB0 = check_bit(IRT,12) or not self.SC
		DB = self.R
		W_R = check_bit(IRT,1) or self.R
		if AB0:
			if AB1:
				ADR = INTERRUPT_ADDRESS
			else:
				ADR = self.PC
		else:
			ADR = self.AR
		## ALU
		F = (int(self.S)<<0)|(int(self.IEN)<<1)|(int(self.E)<<2)|(int(self.B)<<3)
		F |=(int(self.FG1)<<4)|(int(self.FG2)<<5)|(int(self.FG3)<<6)|(int(self.FG4)<<7)
		ALU = [
			self.AC,
			self.MEM[ADR],
			~(self.AC & self.MEM[ADR]),
			self.AC + self.MEM[ADR],

			(self.AC & 0xFF00) | (self.INPR% 2**8),
			F,
			int("".join(list('{0:b}'.format(self.AC))[::-1]).ljust(16,'0'),2),
			(self.AC << 1) | (int(self.E)),
		][ALU_DS]
		C = [check_bit(ALU,15),check_bit(self.AC,15)][ALU_CS]
		##FLU
		FLU = [
			self.AC,
			self.AC | F,
			self.AC & F,
			self.AC ^ F,
		][FLU_CS]
		#handle synchronus
		##handle internal
		R = (self.FG1 or self.FG2 or self.FG3 or self.FG4) and self.SC and self.IEN

		if self.S:
			SC = (not self.SC) and not self.R
		else:
			SC = self.SC
		##handle flags
		if check_bit(IRT,5):
			S = check_bit(FLU,0)
			IEN = check_bit(FLU,1)
			E = check_bit(FLU,2)
			B = check_bit(FLU,3)
			FG1 = check_bit(FLU,4)
			FG2 = check_bit(FLU,5)
			FG3 = check_bit(FLU,6)
			FG4 = check_bit(FLU,7)
		else:
			S = self.S
			IEN = self.IEN
			E = self.E
			B = self.B
			FG1 = self.FG1
			FG2 = self.FG2
			FG3 = self.FG3
			FG4 = self.FG4
		
		if check_bit(IRT,14) and check_bit(IRT,13):
			E = C or (check_bit(FLU,2) and check_bit(IRT,5))
		
		if R:
			IEN = False
		
		#handle registers
		AR = self.AR
		AC = self.AC
		PC = self.PC
		IR = self.IR
		OUTR = self.OUTR

		if AR_EN:
			AR = self.MEM[ADR]
		if AC_EN:
			AC = ALU
		if PC_EN:
			PC = self.AR
		elif PC_INC:
			PC = self.PC+1
		elif PC_CLR:
			PC = 0
		if IR_EN:
			IR = self.MEM[ADR]
		if OUTR_EN:
			OUTR = self.AC
		if W_R:
			NEW_MEM = [self.AC,self.PC][int(DB)]

		#update state
		#data
		#registers
		self.AR = AR % 2**16
		self.AC = AC % 2**16
		self.PC = PC % 2**16
		self.IR = IR % 2**16
		self.OUTR = OUTR % 2**8
		#flags
		self.S = S
		self.IEN = IEN
		self.E = E
		self.B = B
		self.FG1 = FG1
		self.FG2 = FG2
		self.FG3 = FG3
		self.FG4 = FG4
		#internal
		self.SC = SC
		self.R = R
		#Memory
		if W_R:
			self.MEM[ADR] = NEW_MEM
def word_to_hex(x):
	return "0x"+hex(x)[2:].rjust(4,"0").upper()
def print_hex(txt,x):
	print(txt,word_to_hex(x))

#test
# processor = Processor(True,True)
# for i in range(50):
# 	processor.cycle()
# 	print('-'*10)
# 	print_hex('AC:',processor.AC)
# 	print_hex('IR:',processor.IR)
# print_hex('OUTR:',processor.OUTR)