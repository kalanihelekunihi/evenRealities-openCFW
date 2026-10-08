from pathlib import Path
import sys,json,hashlib,struct,itertools,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;fw=(D.parents[2]/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';elf=Path(sys.argv[1]);segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);pc=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='touch_gesture_speed');segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
visited=set()
def run(native,state,position,stamp,mask,null=False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x10000);u.mem_write(0x3300,fw[32:])
 for a,b in segments:u.mem_write(a,b)
 u.mem_write(0x20006000,bytes(state))
 def code(u,a,n,user):
  if 0x3efc<=a<0x4040:visited.update(range(a,a+n))
 if not native:u.hook_add(UC_HOOK_CODE,code,begin=0x3efc,end=0x403e)
 for reg,v in [(UC_ARM_REG_R0,0 if null else 0x20006000),(UC_ARM_REG_R1,position),(UC_ARM_REG_R2,stamp),(UC_ARM_REG_SP,0x20008000),(UC_ARM_REG_LR,0x20000001),(UC_ARM_REG_PRIMASK,mask)]:u.reg_write(reg,v)
 u.emu_start((pc if native else 0x3efc)|1,0x20000000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return {'return':u.reg_read(UC_ARM_REG_R0),'state':u.mem_read(0x20006000,80).hex(),'sp':u.reg_read(UC_ARM_REG_SP),'primask':u.reg_read(UC_ARM_REG_PRIMASK)}
rng=random.Random(20261008);cases=[]
for index,count,filtered,direction,pair in itertools.product(range(3),range(4),[0,1,100,255],[-1,0,1],[(0,0),(0,255),(100,97),(100,96),(100,103),(100,104),(255,0)]):
 for elapsed in [0,1,2,100,0xffffffff]:
  state=bytearray(rng.randbytes(80));state[72:76]=bytes([index,count,filtered,direction&255]);previous=(index+2)%3;oldposition,position=pair;state[48+previous*8]=oldposition;struct.pack_into('<I',state,52+previous*8,100);stamp=(100+elapsed)&0xffffffff;mask=index&1;a=run(False,state,position,stamp,mask);b=run(True,state,position,stamp,mask);assert a==b,(index,count,filtered,direction,pair,elapsed,a,b);cases.append({'inputs':[index,count,filtered,direction,pair,elapsed,mask],'result':a})
for mask in [0,1]:
 state=bytes(80);a=run(False,state,0,0,mask,True);b=run(True,state,0,0,mask,True);assert a==b;cases.append({'inputs':['null',mask],'result':a})
r={'status':'PASS_INDEPENDENT_NATIVE_ORIGINAL_SPEED_NO_FUNCTION_CUTS','cases':len(cases),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'original_instruction_bytes_visited':len(visited),'coverage':sorted(visited),'comparisons':cases,'limits':['Valid ringindex0..2,count0..3,positionbyte; other statebytes varied deterministically.','No function-entry cuts/MMIO/SROM effects; original memory/division/logger instructions execute, native is standalone source.','Counter arithmetic compared, not physical timing or analog speed units.']};(D/'results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'speed cases;',len(visited),'original bytes covered')
