ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUMERIC = "0123456789"
HEXADECIMAL = "0123456789ABCDEF"
MEMORY_SIZE = 2**16
CMDS = {
  "SAR" : b'\x00\x01',
  "STA" : b'\x00\x02',

  "JMP" : b'\x00\x04',
  "SIZ" : b'\x00\x08',

  "OUT" : b'\x00\x10',
  
  "STF" : b'\x00\x20',
  "ORF" : b'\x00\x60',
  "ANF" : b'\x00\xA0',
  "XRF" : b'\x00\xE0',

  "RAS" : b'\x10\x00',

  "TRN" : b'\x00\x00',
  "LDA" : b'\x20\x00',
  "NND" : b'\x40\x00',
  "ADD" : b'\x60\x00',
  "LDI" : b'\x80\x00',
  "LDF" : b'\xA0\x00',
  "INV" : b'\xC0\x00',
  "CIL" : b'\xE0\x00',
  }

def first_pass(file):
  new_text = []
  labels=dict()
  location = 0
  for line in file:
    new_location,is_org = check_org(line,location)
    #handle comments
    line = line.split("/",1)[0].strip()
    if not line:
      continue
    if not is_org:
      tokens = line.split(",")
      #handle labeling
      if len(tokens) !=1:
        i_label = tokens.pop(0).strip()
        label = add_lbl(i_label)
        if label:
          labels[label]=location.to_bytes(2,"big",signed = False)
      #handle direct referencing
      tokens = tokens[0].strip().split()
      command = tokens.pop(0)
      if tokens:
        new_text.append(command+'V')
        new_text.append(tokens[0])
        new_location+=1
      elif len(command) > 3 and command[3] == '>':
        tokens = command.split('>')
        new_text.append('SARV')
        new_text.append(tokens[1])
        new_text.append(tokens[0])
        new_location+=2
      else:
        new_text.append(command)
    else:
      new_text.append(line)
    location = new_location
  return new_text,labels

def check_org(line,location):
  line = line.strip()
  if line.startswith("ORG"):
    location = int(line.split(maxsplit=1)[1],16)
    if location >= MEMORY_SIZE:
      raise Exception("address sepcified is too large or unintelligible")
    else:
      return location,True
  else:
    return location+1,False

def add_lbl(label):
  if len(label) ==0:
    raise Exception(f'label name "{label}" is missing')
  elif len(label) > 3:
    raise Exception(f'label name "{label}" is too long')
  elif not all(((char in ALPHA) or (char in NUMERIC)) for char in label):
    raise Exception(f'label name "{label}" contains unallowed characters')
  elif label in NUMERIC:
    raise Exception(f'label name "{label}" starts with a number')
  else:
    return label

def second_pass(first_pass_result):
  lines,labels = first_pass_result
  print(lines)
  program = bytearray(b'\x00\x00')*(MEMORY_SIZE)
  location = 0
  for line in lines:
    new_location,is_org= check_org(line,location)
    if not is_org:
      code = to_code(line,labels)
      if code ==None:
        return program
      else:
        program[location*2]=code[0]
        program[location*2+1]=code[1]
    location = new_location
  return program

def to_code(line,labels):
  if line == "END":
    return None
  elif line in CMDS:
    cmd = CMDS[line]
    return cmd
  elif line[:-1] in CMDS and line[-1] == 'V':
    cmd = CMDS[line[:-1]]
    return [cmd[0]|0x10, cmd[1]]
  elif line in labels:
    return labels[line]
  elif line[0] in HEXADECIMAL or line[0] == "-":
    #Handle numbers
    if line.endswith(("H")):
      if line.startswith("-"):
        return int(line[:-1],16).to_bytes(2,"big",signed = True)
      else:
        return int(line[:-1],16).to_bytes(2,"big",signed = False)
    elif line[0] in NUMERIC or (line[1] in NUMERIC and line.startswith("-")):
      if line.startswith("-"):
        return int(line,10).to_bytes(2,"big",signed = True)
      else:
        return int(line,10).to_bytes(2,"big",signed = False)
    else:
      raise Exception(f'hexadecimal value with no H identifier : {line}')
  else:
    raise Exception(f'unintelligable command or label : {line}')

def display_hex_code(code):
  skipping = False
  last_hex_code = 'xxxx'
  for i in range(len(code)//2):
    hex_code = hex(code[2*i]*256+code[2*i+1])[2:].rjust(4,"0")
    if hex_code == last_hex_code:
      skipping = True
    else:
      last_hex_code = hex_code
      if skipping:
        print("\t\t...")
      skipping = False
      print("0x"+hex(i)[2:].rjust(4,"0").upper(),hex_code.upper(),sep="\t")

def run(file_in,file_out):
  with open(file_in) as inputfile:
    program = second_pass(first_pass(inputfile))
    display_hex_code(program)
    with open(file_out,"wb") as output_file:
      output_file.write(program)
if __name__ == '__main__':
  run("code.asm",'code.bin')