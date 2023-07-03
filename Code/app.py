from sys import exit
from PyQt6.QtCore import (
	Qt,
	QTimer
	)
from PyQt6.QtWidgets import (
	QApplication,
	QGridLayout,
	QLineEdit,
	QLabel,
	QMainWindow,
	QPushButton,
	QVBoxLayout,
	QHBoxLayout,
	QWidget,
)
from functools import partial
from tooltips import tooltips
import assembler
import emulator
import styleSheets
WINDOW_SIZE = (1024,512+256)
BUTTON_SIZE = (24,24)
MEM_BUTTON_SIZE = (64,20)
def full_hex(x):
	return '0x'+hex(x).upper()[2:].rjust(4,'0')

class PyEWindow(QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		#changable
		self.setWindowTitle("PyEmulator")
		self.setFixedSize(*WINDOW_SIZE)
		self.generalLayout = QHBoxLayout()
		self.leftPanel = QWidget()
		self.leftPanel.setLayout(QVBoxLayout())
		self.generalLayout.addWidget(self.leftPanel)
		#-----
		self.setStyleSheet(styleSheets.general_style)
		centrawidget = QWidget(self)
		centrawidget.setLayout(self.generalLayout)
		self.cBook = {}
		self.setCentralWidget(centrawidget)
		self._createSettingsPanel()
		self._createInterfacePanel()
		self._createMemoryPanel()
		# for key,val in self.cBook.items():
		# 	if key == 'Mem':
		# 		print(f'{key}:[...]')
		# 	else:
		# 		print(f'{key}:{val}')
	
	def createBBox(self,copmonents,H=False,cBookID = None) ->QWidget:
		widget = QWidget()
		layout = QHBoxLayout() if H else QVBoxLayout()
		widget.setLayout(layout)
		for comp in copmonents:
			widget.layout().addWidget(comp)
		if cBookID:
			self.cBook[cBookID] = widget
		return widget
	
	def createGBox(self,grid_size = (8,32),cBookID = None) ->QWidget:
		widget = QWidget()
		layout = QGridLayout()
		layout.setHorizontalSpacing(0)
		btns = []
		widget.setLayout(layout)
		for r in range(grid_size[1]):
			btns.append([])
			for c in range(grid_size[0]):
				btn = QPushButton()
				btn.setText('A1F0')
				btn.setFixedSize(*MEM_BUTTON_SIZE)
				widget.layout().addWidget(btn,r,c)
				btns[-1].append(btn)
		if cBookID:
			self.cBook[cBookID] = btns
		return widget

	def createLabel(self,text,cBookID = None)->QLabel:
		widget = QLabel()
		widget.setText(text)
		if cBookID:
			self.cBook[cBookID] = widget
		return widget

	def createLineEdit(self,ro = False,cBookID = None)->QLineEdit:
		widget = QLineEdit()
		if cBookID:
			self.cBook[cBookID] = widget
		if ro:
			widget.setReadOnly(True)
		return widget

	def createButton(self,text = '',checkable=False,cBookID = None)->QPushButton:
		widget = QPushButton()
		widget.setFixedSize(*BUTTON_SIZE)
		widget.setText(text)
		widget.setCheckable(checkable)
		if cBookID:
			self.cBook[cBookID] = widget
		return widget

	def createRegisterControl(self,text,addressable = False,cBookID = None)->QWidget:
		widget = self.createBBox(
					[
						self.createLabel(text),
						self.createLineEdit(cBookID=cBookID+'_value'),
						self.createLineEdit(ro = True,cBookID=cBookID+'_decoded'),
						self.createButton('D',cBookID=cBookID+'_switch'),
					],
					H = True,
				)
		widget.setFixedHeight(64)
		if addressable:
			widget.layout().addWidget(self.createButton('J',cBookID=cBookID+'_jump'))
		if cBookID:
			self.cBook[cBookID] = widget
		return widget

	def _createSettingsPanel(self):

		panel = self.createBBox(
			[
				self.createLabel('Emulation Settings'),
				self.createBBox(
					[
						self.createLabel('speed'),
						self.createLineEdit(cBookID="Emul_speed"),
						self.createLabel('toggle S flag on play'),
						self.createButton(cBookID="Emul_AutoFlag"),
					],
					H = True
				),
				self.createBBox(
				[
					self.createButton('P',cBookID="Emul_P"),
					self.createButton('S',cBookID="Emul_C"),
					self.createButton('R',cBookID="Emul_R"),
					self.createLabel('Binary file path:'),
					self.createLineEdit(cBookID="Emul_path"),
					self.createButton('L',cBookID="Emul_L"),
				],
				H = True
				),
				self.createLabel('Asembler Settings'),
				self.createBBox(
				[
					self.createLabel('Input File Path:'),
					self.createLineEdit(cBookID="ASM_input_path"),
					self.createLabel('Output File Path:'),
					self.createLineEdit(cBookID="ASM_output_path"),
				],
				),
				self.createBBox(
				[
					self.createLabel('Assemble:'),
					self.createButton('>_',cBookID = 'ASM'),
					self.createLabel('Console Output:'),
				],
				H = True
				),
				self.createLineEdit(cBookID="ASM_console_output"),
			],
			H = False
		)
		self.leftPanel.layout().addWidget(panel)
		self.settingsPanel = panel
	
	def _createInterfacePanel(self):
		panel = self.createBBox(
			[
				self.createLabel('Register Interface'),
				self.createBBox(
					[
						self.createLabel('Interface'),
						self.createButton('S',cBookID="IO_S"),
						self.createButton('IO1',cBookID="IO_1"),
						self.createButton('IO2',cBookID="IO_2"),
						self.createButton('IO3',cBookID="IO_3"),
						self.createButton('IO4',cBookID="IO_4"),
					],
					H = True
				),
				self.createBBox(
					[
						self.createLabel('Flags'),
						self.createButton('FG4',True,cBookID="F_FG4"),
						self.createButton('FG3',True,cBookID="F_FG3"),
						self.createButton('FG2',True,cBookID="F_FG2"),
						self.createButton('FG1',True,cBookID="F_FG1"),
						self.createButton('B',True,cBookID="F_B"),
						self.createButton('E',True,cBookID="F_E"),
						self.createButton('IEN',True,cBookID="F_IEN"),
						self.createButton('S',True,cBookID="F_S"),
					],
					H = True
				),
				self.createRegisterControl('INPR',False,'INPR'),
				self.createRegisterControl('OUTR',False,'OUTR'),
				self.createRegisterControl('PC',True,'PC'),
				self.createRegisterControl('IR',False,'IR'),
				self.createRegisterControl('AR',True,'AR'),
				self.createRegisterControl('AC',False,'AC'),
			],
			H = False
		)
		self.leftPanel.layout().addWidget(panel)
		self.interfacePanel = panel
	
	def _createMemoryPanel(self):
		side_labels = []
		for i in range(32):
			lbl = self.createLabel('xx'+hex(i*8).upper()[2:].rjust(2,'0'))
			lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
			lbl.setFixedSize(40,20)
			side_labels.append(lbl)
		labels = self.createBBox(side_labels,H=False)
		gbox = self.createGBox(cBookID = 'Mem')
		gbox.setStyleSheet(styleSheets.mem_buttons)
		panel = self.createBBox(
			[
				self.createLabel('Memory manager'),
				self.createBBox(
					[
						self.createLabel('data'),
						self.createLineEdit(cBookID = 'M_Value'),
						self.createLabel('',cBookID = 'M_Decoded'),
					],
					H = True
				),
				self.createBBox(
					[
						self.createButton('<H',cBookID = 'M_L3'),
						self.createButton('<<',cBookID = 'M_L2'),
						self.createButton('<',cBookID = 'M_L1'),
						self.createLineEdit(cBookID = 'M_Block'),
						self.createButton('>',cBookID = 'M_R1'),
						self.createButton('>>',cBookID = 'M_R2'),
						self.createButton('H>',cBookID = 'M_R3'),
					],
					H = True
				),
				self.createBBox(
					[
						labels,
						gbox,
					]
					,H=True),
				
			],
			H = False
		)
		self.cBook['M_Block'].setText('00')
		self.generalLayout.addWidget(panel)
		self.memoryPanel = panel

	#lineEdit properties
		# setFixedHeight(DISPLAY_HEIGHT)
		# setAlignment(Qt.AlignmentFlag.AlignRight)
		# setReadOnly(True)

class PyEController():
	def __init__(self,window:PyEWindow) -> None:
		self.window = window
		self.emulation = emulator.Processor('code.bin',True)
		self.cBook = self.window.cBook
		self.cBook["Emul_path"].setText('code.bin')
		self.cBook["ASM_input_path"].setText('code.asm')
		self.cBook["ASM_output_path"].setText('code.bin')
		self.memory_block = 0
		self.cycle_timer = QTimer()
		self.auto_flag = True
		self.cBook["Emul_AutoFlag"].setCheckable(True)
		self.cBook["Emul_AutoFlag"].setChecked(True)
		self.running = False
		self.cBook["Emul_speed"].setText('500')
		self.cBook['ASM_console_output'].setReadOnly(True)
		self.update_emulation_speed()
		self.select_memory_location(0)
		self.connect_functions()
		self.update_view()
		self.set_tooltips()


	def connect_functions(self):
		self.cycle_timer.timeout.connect(partial(self.update_cycle))
		self.cBook["M_Block"].editingFinished.connect(self.update_memory_block_from_text)
		self.cBook["M_Value"].editingFinished.connect(self.update_memory_value)
		self.cBook["M_R1"].clicked.connect(partial(self.set_memory_block,1,True))
		self.cBook["M_R2"].clicked.connect(partial(self.set_memory_block,4,True))
		self.cBook["M_R3"].clicked.connect(partial(self.set_memory_block,16,True))
		self.cBook["M_L1"].clicked.connect(partial(self.set_memory_block,-1,True))
		self.cBook["M_L2"].clicked.connect(partial(self.set_memory_block,-4,True))
		self.cBook["M_L3"].clicked.connect(partial(self.set_memory_block,-16,True))
		self.cBook["Emul_C"].clicked.connect(partial(self.update_cycle))
		self.cBook["Emul_R"].clicked.connect(self.reset_emulation)
		self.cBook["ASM"].clicked.connect(self.assemble)

		self.cBook["Emul_AutoFlag"].clicked.connect(self.update_auto_flag)
		self.cBook["Emul_speed"].editingFinished.connect(self.update_emulation_speed)
		self.cBook["Emul_P"].clicked.connect(partial(self.run_timer))
		self.cBook["Emul_L"].setCheckable(True)
		self.cBook["Emul_L"].clicked.connect(self.update_binary_link)
		#interface
		self.cBook['F_FG1'].clicked.connect(partial(self.set_flag,'FG1'))
		self.cBook['F_FG2'].clicked.connect(partial(self.set_flag,'FG2'))
		self.cBook['F_FG3'].clicked.connect(partial(self.set_flag,'FG3'))
		self.cBook['F_FG4'].clicked.connect(partial(self.set_flag,'FG4'))
		
		self.cBook['F_S'].clicked.connect(partial(self.set_flag,'S'))
		self.cBook['F_IEN'].clicked.connect(partial(self.set_flag,'IEN'))
		self.cBook['F_E'].clicked.connect(partial(self.set_flag,'E'))
		self.cBook['F_B'].clicked.connect(partial(self.set_flag,'B'))
		self.cBook['F_FG1'].clicked.connect(partial(self.set_flag,'FG1'))
		self.cBook['F_FG2'].clicked.connect(partial(self.set_flag,'FG2'))
		self.cBook['F_FG3'].clicked.connect(partial(self.set_flag,'FG3'))
		self.cBook['F_FG4'].clicked.connect(partial(self.set_flag,'FG4'))
		self.cBook['IO_S'].clicked.connect(partial(self.set_property,'set_S',True))
		self.cBook['IO_1'].clicked.connect(partial(self.set_property,'set_FG1',True))
		self.cBook['IO_2'].clicked.connect(partial(self.set_property,'set_FG2',True))
		self.cBook['IO_3'].clicked.connect(partial(self.set_property,'set_FG3',True))
		self.cBook['IO_4'].clicked.connect(partial(self.set_property,'set_FG4',True))
		self.cBook['PC_jump'].clicked.connect(partial(self.jump_to_register_address,'PC_value'))
		self.cBook['AR_jump'].clicked.connect(partial(self.jump_to_register_address,'AR_value'))

		self.cBook["AR_value"].editingFinished.connect(partial(self.set_register,'AR'))
		self.cBook["IR_value"].editingFinished.connect(partial(self.set_register,'IR'))
		self.cBook["PC_value"].editingFinished.connect(partial(self.set_register,'PC'))
		self.cBook["AC_value"].editingFinished.connect(partial(self.set_register,'AC'))
		self.cBook["INPR_value"].editingFinished.connect(partial(self.set_register,'INPR'))
		self.cBook["OUTR_value"].editingFinished.connect(partial(self.set_register,'OUTR'))

		for r,row in enumerate(self.window.cBook["Mem"]):
			for c,btn in enumerate(row):
				btn.clicked.connect(partial(self.select_memory_location,r*8+c))

	def set_tooltips(self):
		for key,widget in self.cBook.items():
			if key != 'Mem':
				widget.setToolTip(tooltips.get(key,''))

	def update_auto_flag(self):
		self.auto_flag = self.cBook['Emul_AutoFlag'].isChecked()

	def update_emulation_speed(self):
		try:
			self.time_per_frame = int(self.cBook["Emul_speed"].text())
		except Exception:
			pass

	def pause_timer(self):
		self.running = False
		self.cycle_timer.stop()
		self.cBook['IR_value'].setReadOnly(False)
		self.cBook['AR_value'].setReadOnly(False)
		self.cBook['AC_value'].setReadOnly(False)
		self.cBook['PC_value'].setReadOnly(False)
		self.cBook['INPR_value'].setReadOnly(False)
		self.cBook['OUTR_value'].setReadOnly(False)
		# self.cBook['F_S'].setEnabled(True)
		# self.cBook['F_IEN'].setEnabled(True)
		# self.cBook['F_E'].setEnabled(True)
		# self.cBook['F_B'].setEnabled(True)
		# self.cBook['F_FG1'].setEnabled(True)
		# self.cBook['F_FG2'].setEnabled(True)
		# self.cBook['F_FG3'].setEnabled(True)
		# self.cBook['F_FG4'].setEnabled(True)

	def jump_to_register_address(self,cBookID):
		self.jump_to_address(int(self.cBook[cBookID].text(),16))

	def jump_to_address(self,address):
		self.set_memory_block(address//2**8,False)
		self.select_memory_location(address%2**8)

	def set_flag(self,ID):
		self.set_property(ID,self.cBook['F_'+ID].isChecked())
	
	def set_register(self,ID):
		try:
			setattr(self.emulation,ID,int(self.cBook[ID+'_value'].text(),16))
		except Exception:
			pass

	def set_property(self,ID,value):
		setattr(self.emulation,ID,value)

	def assemble(self):
		try:
			assembler.run(self.cBook["ASM_input_path"].text(),self.cBook["ASM_output_path"].text())
		except Exception as err:
			self.cBook["ASM_console_output"].setText(str(err))
		else:
			self.cBook["ASM_console_output"].setText('code assembled succefully')

	def set_memory_block(self,location,additive = True):
		if additive:
			location = min(2**8-1,max(0,location+self.memory_block))
		self.memory_block = location
		self.cBook["M_Block"].setText(hex(int(self.memory_block ))[2:].rjust(2,'0').upper())
		self.update_memory_block()

	def reset_emulation(self):
		self.pause_timer()
		self.emulation.reset(self.cBook["Emul_path"].text(),self.auto_flag)
		self.update_view()
	
	def select_memory_location(self,location):
		self.selected_memory_location = location
		self.update_memory_selection()

	def update_memory_selection(self):
		self.cBook["M_Value"].setText(full_hex(self.emulation.MEM[self.selected_memory_location+self.memory_block*2**8]))

	def update_memory_block_from_text(self):
		try:
			memory_block = hex(int(self.cBook["M_Block"].text(),16))[2:]
		except:
			memory_block = None
		
		if not memory_block or len(memory_block)>2:
			memory_block = '00'
			self.cBook["M_Block"].setText(memory_block)
		self.memory_block = int(memory_block,16)
		self.cBook["M_Block"].setText(hex(int(self.memory_block ))[2:].rjust(2,'0').upper())
		self.update_memory_block()

	def update_memory_value(self):
		try:
			self.emulation.MEM[self.selected_memory_location+self.memory_block*2**8] = int(self.cBook["M_Value"].text(),16)
		except:
			self.cBook["M_Value"].setText(full_hex(self.emulation.MEM[self.selected_memory_location+self.memory_block*2**8]))
		self.update_memory_block()

	def update_memory_block(self):
		self.update_memory_selection()
		for r,row in enumerate(self.window.cBook["Mem"]):
			for c,btn in enumerate(row):
				btn.setText(emulator.word_to_hex(self.emulation.MEM[self.memory_block*2**8+r*8+c]))
	
	def update_view(self):
		self.update_memory_block()
		self.cBook['IR_value'].setText(emulator.word_to_hex(self.emulation.IR))
		self.cBook['AR_value'].setText(emulator.word_to_hex(self.emulation.AR))
		self.cBook['AC_value'].setText(emulator.word_to_hex(self.emulation.AC))
		self.cBook['PC_value'].setText(emulator.word_to_hex(self.emulation.PC))
		self.cBook['INPR_value'].setText(emulator.word_to_hex(self.emulation.INPR))
		self.cBook['OUTR_value'].setText(emulator.word_to_hex(self.emulation.OUTR))
		self.cBook['F_S'].setChecked(self.emulation.S)
		self.cBook['F_IEN'].setChecked(self.emulation.IEN)
		self.cBook['F_E'].setChecked(self.emulation.E)
		self.cBook['F_B'].setChecked(self.emulation.B)
		self.cBook['F_FG1'].setChecked(self.emulation.FG1)
		self.cBook['F_FG2'].setChecked(self.emulation.FG2)
		self.cBook['F_FG3'].setChecked(self.emulation.FG3)
		self.cBook['F_FG4'].setChecked(self.emulation.FG4)

	def update_binary_link(self):
		if self.cBook['Emul_L'].isChecked():
			self.cBook['Emul_path'].setEnabled(False)
			self.cBook['Emul_path'].setText(self.cBook['ASM_output_path'].text())
		else:
			self.cBook['Emul_path'].setEnabled(True)

	def run_timer(self):
		if self.running:
			self.pause_timer()
			return
		self.running = True
		self.cycle_timer.start(self.time_per_frame)
		self.cBook['IR_value'].setReadOnly(True)
		self.cBook['AR_value'].setReadOnly(True)
		self.cBook['AC_value'].setReadOnly(True)
		self.cBook['PC_value'].setReadOnly(True)
		self.cBook['INPR_value'].setReadOnly(True)
		self.cBook['OUTR_value'].setReadOnly(True)
		# self.cBook['F_S'].setEnabled(False)
		# self.cBook['F_IEN'].setEnabled(False)
		# self.cBook['F_E'].setEnabled(False)
		# self.cBook['F_B'].setEnabled(False)
		# self.cBook['F_FG1'].setEnabled(False)
		# self.cBook['F_FG2'].setEnabled(False)
		# self.cBook['F_FG3'].setEnabled(False)
		# self.cBook['F_FG4'].setEnabled(False)

	def update_cycle(self):
		self.emulation.cycle()
		self.update_view()
		if self.running:
			self.cycle_timer.start(self.time_per_frame)
			
		


def main():
	pyEApp = QApplication([])
	pyEWindow = PyEWindow()
	pyEController = PyEController(pyEWindow)
	pyEWindow.show()
	exit(pyEApp.exec())

if __name__ == "__main__":
	main()