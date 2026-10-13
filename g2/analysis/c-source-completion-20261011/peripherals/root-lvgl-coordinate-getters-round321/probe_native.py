from pathlib import Path
import json,hashlib,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;blob=Path('/tmp/opencfw-main-native.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
for address in [0x200000,0x200020,0x200040,0x200060,0x200080]:u.mem_write(address,b'\x70\x47')
with (D/'candidate.elf').open('rb') as f:
 e=ELFFile(f)
 for sec in e.iter_sections():
  if sec['sh_flags']&2 and sec['sh_type']!='SHT_NOBITS':u.mem_write(sec['sh_addr'],sec.data())
 symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12340000+i*0x101 for i in range(8)];calls=[];faults=[];spaces=[]
def cstring(pointer):
 out=bytearray()
 for i in range(512):
  c=u.mem_read(pointer+i,1)[0]
  if not c:return out.decode()
  out.append(c)
 raise AssertionError('No string terminator')
children={0x43efc6:0,0x43eff4:1,0x43f022:2,0x43f050:3,0x200020:0,0x200040:1,0x200060:2,0x200080:3}
def code(uc,address,size,user):
 if address in children:
  index=children[address];calls.append(('space',index,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_R0,spaces[index]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 elif address in [0x44d25c,0x200000]:
  sp=uc.reg_read(UC_ARM_REG_SP);stack=struct.unpack('<3I',uc.mem_read(sp,12));calls.append(('log',uc.reg_read(UC_ARM_REG_R0),cstring(uc.reg_read(UC_ARM_REG_R1)),uc.reg_read(UC_ARM_REG_R2),cstring(uc.reg_read(UC_ARM_REG_R3)),*(cstring(v) for v in stack)));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
def invalid(uc,access,address,size,value,user):faults.append((access,address,size,value));return False
u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
def run(entry,obj,out,initial):
 calls.clear();faults.clear();u.mem_write(0x20005000,initial);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,out)
 for reg,value in zip(regs,seeds):u.reg_write(reg,value)
 u.mem_write(0x200ff000,b'\xa5'*16)
 try:u.emu_start(entry|1,0x600000,count=2000)
 except UcError:
  assert obj==0 and faults
 if obj:
  assert not faults and u.reg_read(UC_ARM_REG_PC)==0x600000 and u.reg_read(UC_ARM_REG_SP)==0x200ff000
  assert [u.reg_read(r) for r in regs]==seeds
 assert bytes(u.mem_read(0x200ff000,16))==b'\xa5'*16
 return list(calls),list(faults),bytes(u.mem_read(0x20005000,192))
rng=random.Random(321);count=0
for native,name in [(0x43fc2a,'audio_uart_lv_obj_coords_43fc2a'),(0x43feca,'audio_uart_lv_obj_content_coords_43feca')]:
 for trial in range(384):
  initial=bytes(rng.getrandbits(8) for _ in range(192));obj=0x20005020;out=obj+20+[0,4,8,-4,-8,64][trial%6];spaces=[rng.getrandbits(32) for _ in range(4)]
  expected=run(native,obj,out,initial);actual=run(symbols[name],obj,out,initial);assert actual==expected,(name,trial,expected,actual)
  assert actual[0]==([('space',i,obj,0) for i in range(4)] if native==0x43feca else [])
  count+=1
 spaces=[0]*4;expected=run(native,0,0x20005080,bytes(192));actual=run(symbols[name],0,0x20005080,bytes(192));assert actual==expected,(name,'null',expected,actual)
 assert expected[1][0][1:]==(0xffffffff,4,0) and expected[0][0][0:2]==('log',3)
 count+=1
receipt={'status':'PASS_COMPLETE_COORDINATE_GETTER_BODIES','native_comparisons':count,'nonnull_cases':768,'null_assertion_cases':2,'controlled_children':['diagnostic log44d25c','four space getters43efc6/43eff4/43f022/43f050'],'actual_copy_child_executed':True,'checks':['full192byte object/output guard','alias overlap','ordered object/part calls','32bit wrap','SP/callee seeds/caller guard','all diagnostic strings/line/level','native null fault address/width/value'],'selected':False,'candidate_sha256':hashlib.sha256((D/'candidate-unadmitted.c').read_bytes()).hexdigest(),'limits':['Space property engine and diagnostic backend controlled, not qualified by these probes','Physical fault handler/concurrency/unaligned pointers/full image unproven']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
