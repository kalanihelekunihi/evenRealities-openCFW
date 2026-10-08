from pathlib import Path
import itertools,json,struct,hashlib,sys
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
D=Path(__file__).resolve().parent;ROOT=D.parents[2];b=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';b=b[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={};cs=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
def run(native,reg,entry,cr1,scr,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x08000000,0x10000);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000);u.mem_map(0xe000e000,0x1000)
 if native:
  for addr,raw in segments:u.mem_write(addr,raw)
 else:u.mem_write(0x08000000,b)
 for addr,v in [(0x40007000,cr1),(0xe000ed10,scr)]:u.mem_write(addr,struct.pack('<I',v))
 for r,v in [(UC_ARM_REG_R0,reg),(UC_ARM_REG_R1,entry),(UC_ARM_REG_PRIMASK,mask),(UC_ARM_REG_SP,0x20008000),(UC_ARM_REG_LR,0x20000001)]:u.reg_write(r,v)
 events=[]
 def code(u,pc,size,user):
  ins=next(cs.disasm(bytes(u.mem_read(pc,size)),pc))
  if ins.mnemonic in ['sev','wfe','wfi']:
   events.append(['wait-instruction',ins.mnemonic])
   if ins.mnemonic in ['wfi','wfe']:u.reg_write(UC_ARM_REG_PC,(pc+size)|1)
 def write(u,access,addr,size,value,user):
  if addr in [0x40007000,0xe000ed10]:events.append(['write',addr,size,value])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((symbols['case_stop_mode'] if native else 0x080050e8)|1,0x20000000,count=500);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return dict(events=events,cr1=int.from_bytes(u.mem_read(0x40007000,4),'little'),scr=int.from_bytes(u.mem_read(0xe000ed10,4),'little'),sp=u.reg_read(UC_ARM_REG_SP),primask=u.reg_read(UC_ARM_REG_PRIMASK))
cases=[]
for vals in itertools.product([0,1,0xffffffff],[0,1,2,0x101],[0,0xffffffff,0x12345678],[0,4,0xa5a5a5a5],[0,1]):
 x=run(False,*vals);y=run(True,*vals);assert x==y,(vals,x,y);assert y['cr1']==(vals[2]&~7)|(1 if vals[0] else 0);assert y['scr']==vals[3]&~4;cases.append(dict(inputs=vals,result=y))
r=dict(status='PASS_BOUNDED_CASE_STOP',cases=len(cases),source_sha256=hashlib.sha256((D/'stop_mode.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),stock_body_sha256=hashlib.sha256(b[0x50e8:0x511e]).hexdigest(),comparisons=cases,limits=['Actual stock/source register instructions execute; WFI/WFE are explicit controlled-wake cuts, not executed waits or hardware behavior. SEV is observed and executed.','Synthetic PWR/SCB register RAM only. No elapsed time, actual sleep/wake, clock restart or IRQ delivery proof.','Void raw return and flags outside contract. Raw entry0x101 followsWFE despite public uint8 prototype; no valid-API endorsement.','Public HALv1.4.7 is a behavioral comparator, not a proven source revision or exact stock compiler. Existing catalogue preserved.'])
(D/'results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'STOP register/order cases; wait instructions explicitly modeled')
