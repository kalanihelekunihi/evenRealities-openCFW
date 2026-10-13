from pathlib import Path
import itertools,random,hashlib,json
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
D=Path(__file__).resolve().parent
payload=Path('/tmp/opencfw-main-native.bin').read_bytes()
assert hashlib.sha256(payload).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
u.mem_map(0x400000,0x400000);u.mem_write(0x438000,payload)
u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
with (D/'candidate.elf').open('rb') as f:
 e=ELFFile(f)
 for sec in e.iter_sections():
  if sec['sh_flags']&2 and sec['sh_type']!='SHT_NOBITS':u.mem_write(sec['sh_addr'],sec.data())
 symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
argregs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
callee=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
seeds=[0x12340000+i*0x101 for i in range(8)]
def run(entry,args):
 u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
 for r,v in zip(argregs,args):u.reg_write(r,v&0xffffffff)
 for r,v in zip(callee,seeds):u.reg_write(r,v)
 u.mem_write(0x200ff000,b'\xa5'*16)
 u.emu_start(entry|1,0x600000,count=1000)
 assert u.reg_read(UC_ARM_REG_PC)==0x600000
 assert u.reg_read(UC_ARM_REG_SP)==0x200ff000
 assert [u.reg_read(r) for r in callee]==seeds
 assert bytes(u.mem_read(0x200ff000,16))==b'\xa5'*16
 return u.reg_read(UC_ARM_REG_R0)
values=[0,1,99,100,0x7fffffff,0x80000000,0xffffffff,0x1ffffffe,0x1fffffff,0x20000000,0x20000001,0x2fffffff,0x30000000,0x3ffffffe,0x3fffffff,0xa0000000]
bounds=[0,1,0xffffffff,0x7fffffff,0x80000000,0x1ffffffe,0x1fffffff,0x20000001,0x2fffffff,0x30000000,0xa0000001,0xbffffffe]
refs=[0,1,100,0xffffffff,0x80000000,0x7fffffff,0x12345678,0x87654321]
rng=random.Random(319);cases=list(itertools.product(values,bounds,bounds,refs))+[tuple(rng.getrandbits(32) for _ in range(4)) for _ in range(4096)]
count=0
for native,name in [(0x4408d6,'audio_uart_lv_clamp_width_4408d6'),(0x440968,'audio_uart_lv_clamp_height_440968')]:
 for args in cases:
  expected=run(native,args);actual=run(symbols[name],args)
  if actual!=expected:
   (D/'mismatch.json').write_text(json.dumps({'native':hex(native),'args':[hex(x) for x in args],'expected':hex(expected),'actual':hex(actual)},indent=2));raise AssertionError((native,args,expected,actual))
  count+=1
receipt={'status':'PASS_NATIVE_FULL_CLAMP_BODIES','native_comparisons':count,'cases_per_body':len(cases),'child_cuts':0,'checks':['R0bits','SP','R4-R11 independent seeds','16byte caller stack guard'],'candidate_sha256':hashlib.sha256((D/'candidate-unadmitted.c').read_bytes()).hexdigest(),'native_payload_sha256':hashlib.sha256(payload).hexdigest(),'selected':False,'limits':['APSR/ABI scratch registers not equality contract','Physical hardware and complete image unproven']}
(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
