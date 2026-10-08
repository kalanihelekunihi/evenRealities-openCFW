"""Stock/source instruction comparison against synthetic PWR register RAM."""
from pathlib import Path
import hashlib,json,struct,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11
D=Path(__file__).resolve().parent; ROOT=D.parents[2]
b=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(b).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
b=b[32:];assert hashlib.sha256(b).hexdigest()=='773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677'
elfpath=Path(sys.argv[1]); segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def run(native,enable,arg,a,c):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x08000000,0x10000);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000)
 if native:
  for addr,raw in segments:u.mem_write(addr,raw)
 else:u.mem_write(0x08000000,b)
 u.mem_write(0x20000000,b'\x00\xbe');u.mem_write(0x40007008,struct.pack('<II',a,c));u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_R0,arg)
 for i,r in enumerate(regs):u.reg_write(r,0x11111111*(i+1))
 accesses=[]
 def read(u,access,addr,size,value,user):
  if 0x40007000<=addr<0x40008000:accesses.append(['read',addr,size,int.from_bytes(u.mem_read(addr,size),'little')])
 def write(u,access,addr,size,value,user):
  if 0x40007000<=addr<0x40008000:accesses.append(['write',addr,size,value])
 u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
 pc=symbols['case_wake_enable' if enable else 'case_wake_disable'] if native else (0x080050a8 if enable else 0x08005094)
 u.emu_start(pc|1,0x20000000,count=200)
 assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return dict(registers=list(struct.unpack('<II',u.mem_read(0x40007008,8))),accesses=accesses,callee=[u.reg_read(r) for r in regs],sp=u.reg_read(UC_ARM_REG_SP))
cases=[]
for enable in [False,True]:
 for arg in [0,1,2,4,8,16,32,63,0x100,0x101,0x202,0x3f3f,0xffffffff]:
  for a,c in [(0,0),(0xffffffff,0xffffffff),(0x12345678,0xa5a5a5a5),(0x3f,0)]:
   x=run(False,enable,arg,a,c); y=run(True,enable,arg,a,c);assert x==y,(enable,arg,x,y);cases.append(dict(enable=enable,arg=arg,cr3=a,cr4=c,result=x))
report=dict(status='PASS_BOUNDED_CASE_WAKE',cases=len(cases),source_sha256=hashlib.sha256((D/'case_wake.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),body_hashes={hex(a):hashlib.sha256(b[a:a+n]).hexdigest() for a,n in [(0x5094,14),(0x50a8,24)]},comparisons=cases,limits=['Synthetic PWR register RAM only; no physical pin edges, standby entry, reset or IRQ concurrency.','Actual stock and independent source instructions execute; no child-call stubs.','Callee-saved registers, SP, ordered register accesses compare; void raw R0 and flags are outside contract.','All raw argument values tested are register semantics; malformed arguments are not endorsed as vendor API inputs.','Public HAL v1.4.7 is a behavioral comparator, not a proven stock source revision or exact compiler match.'])
(D/'case-wake-results.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(cases),'original/source instruction cases')
