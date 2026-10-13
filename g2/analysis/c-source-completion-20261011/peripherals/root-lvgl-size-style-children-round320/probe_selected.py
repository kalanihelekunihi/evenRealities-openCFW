from pathlib import Path
import json,hashlib,itertools,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent
blob=Path('/tmp/opencfw-main-native.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x200000);u.mem_write(0x200000,b'\x70\x47');u.mem_map(0x20000000,0x100000)
with (D/'selected.elf').open('rb') as f:
 e=ELFFile(f)
 for sec in e.iter_sections():
  if sec['sh_flags']&2 and sec['sh_type']!='SHT_NOBITS':u.mem_write(sec['sh_addr'],sec.data())
 symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
argsregs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345600+i*0x101 for i in range(8)];calls=[];result_bits=0

def hook(uc,address,size,user):
 if address not in (0x44bdea,0x200000):return
 calls.append(tuple(uc.reg_read(r) for r in argsregs[:3]));uc.reg_write(UC_ARM_REG_R0,result_bits);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE,hook)
def run(entry,args):
 calls.clear();u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
 for reg,value in zip(argsregs,args):u.reg_write(reg,value)
 for reg,value in zip(saved,seeds):u.reg_write(reg,value)
 u.mem_write(0x200ff000,b'\xa5'*16);u.emu_start(entry|1,0x600000,count=100)
 assert u.reg_read(UC_ARM_REG_PC)==0x600000 and u.reg_read(UC_ARM_REG_SP)==0x200ff000
 assert [u.reg_read(r) for r in saved]==seeds and bytes(u.mem_read(0x200ff000,16))==b'\xa5'*16
 return u.reg_read(UC_ARM_REG_R0),list(calls)
rows=json.loads((D/'selector-contracts.json').read_text());count=0
for row in rows:
 native=int(row['entry'],16);name=next(n for n in symbols if n.endswith('_'+format(native,'x')))
 for object,selector,bits in itertools.product([0,0x20003000,0x20005000,0xffffffff],[0,1,0x10000,0xffffffff],[0,1,0x7fffffff,0x80000000,0xffffffff,0x123456ff,0xdeadbeef]):
  result_bits=bits;args=(object,selector,0x76543210,0xaabbccdd);expected=run(native,args);actual=run(symbols[name],args)
  assert actual==expected==(bits&255 if row['narrow_uint8'] else bits,[(object,selector,row['property'])]),(row,args,expected,actual)
  count+=1
rng=random.Random(320);copy_count=0
for delta,trial in itertools.product([-16,-12,-8,-4,0,4,8,12,16,32],range(32)):
 initial=bytes(rng.getrandbits(8) for _ in range(128));source=0x20005020;destination=source+delta;results=[]
 for entry in [0x43ee94,symbols['audio_uart_lv_area_copy_43ee94']]:
  u.mem_write(0x20005000,initial);out=run(entry,(destination,source,0x1234,0x5678));assert not out[1];results.append(bytes(u.mem_read(0x20005000,128)))
 assert results[0]==results[1],(delta,trial)
 independent=bytearray(initial)
 for i in range(4):independent[32+delta+4*i:36+delta+4*i]=independent[32+4*i:36+4*i]
 assert results[0]==independent
 copy_count+=1
receipt={'status':'PASS_NATIVE_STYLE_LEAVES_AND_INTERLEAVED_COPY','selector_comparisons':count,'copy_comparisons':copy_count,'checks':['R0bits/UXTB','ordered property call R0/R1/R2','SP/R4-R11/caller stack guard','full128byte copy guard and independent interleaved overlap model'],'controlled_child_targets':[hex(0x44bdea)],'copy_child_cuts':0,'selected':True,'candidate_sha256':hashlib.sha256((D/'candidate-unadmitted.c').read_bytes()).hexdigest(),'limits':['Style property child controlled for wrapper ABI; real style retrieval/data/assertion behavior not executed','Invalid pointers and unaligned copy outside scope','Full image/hardware unproven']};(D/'selected-probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
