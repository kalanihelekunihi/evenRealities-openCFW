"""Controlled between-store IRQ injection, not observed hardware scheduling."""
from pathlib import Path
import json,hashlib,struct,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
import unicorn.arm_const as ar
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';image=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
CTX=0x200008ec;NEW=0x20003000;OLD=0x20004000;SCB=0x40250000
regs=[getattr(ar,'UC_ARM_REG_R'+str(i)) for i in range(13)]+[ar.UC_ARM_REG_SP,ar.UC_ARM_REG_LR,ar.UC_ARM_REG_XPSR,ar.UC_ARM_REG_PRIMASK]
def run(native,inject):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x10000);u.mem_map(SCB,0x1000)
 if native:
  for addr,raw in segments:u.mem_write(addr,raw)
 else:u.mem_write(0x3300,image)
 def word(a,v):u.mem_write(a,struct.pack('<I',v))
 ctx=bytearray(84);ctx[0]=1;ctx[1]=1;struct.pack_into('<I',ctx,4,0x1001);struct.pack_into('<III',ctx,56,OLD,16,5);u.mem_write(CTX,bytes(ctx));u.mem_write(NEW,b'\xcc'*32);u.mem_write(OLD,b'\xdd'*32)
 for off,v in [(0x300,7),(0x304,7),(0x308,8),(0xfcc,1),(0xfc8,1)]:word(SCB+off,v)
 pending=False;phase='setter';paused=False;trace=[];fifo=list(range(0x40,0x48))
 def code(u,pc,size,user):
  nonlocal paused
  if pending and phase=='setter':paused=True;u.emu_stop()
 def write(u,access,addr,size,value,user):
  nonlocal pending
  if phase=='setter' and addr==CTX+56:pending=True
  if SCB<=addr<SCB+4096:trace.append(['write',addr-SCB,size,value])
 def read(u,access,addr,size,value,user):
  if addr==SCB+0x340:
   v=fifo.pop(0) if fifo else 0;word(addr,v);word(SCB+0x308,len(fifo));trace.append(['pop',v])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_READ,read)
 for reg,val in [(ar.UC_ARM_REG_R0,SCB),(ar.UC_ARM_REG_R1,NEW),(ar.UC_ARM_REG_R2,2),(ar.UC_ARM_REG_R3,CTX),(ar.UC_ARM_REG_SP,0x20008000),(ar.UC_ARM_REG_LR,0x20000001)]:u.reg_write(reg,val)
 api=symbols['Cy_SCB_I2C_SlaveConfigWriteBuf'] if native else 0x9af0;u.emu_start(api|1,0x20000000,count=1000);assert paused
 partial=list(struct.unpack('<III',u.mem_read(CTX+56,12)));assert partial==[NEW,16,5]
 saved={r:u.reg_read(r) for r in regs};resume=u.reg_read(ar.UC_ARM_REG_PC)
 if inject:
  phase='irq';u.reg_write(ar.UC_ARM_REG_R0,SCB);u.reg_write(ar.UC_ARM_REG_R1,CTX);u.reg_write(ar.UC_ARM_REG_SP,0x2000c000);u.reg_write(ar.UC_ARM_REG_LR,0x20000001);u.emu_start((symbols['Cy_SCB_I2C_SlaveInterrupt'] if native else 0x9b0c)|1,0x20000000,count=3000);assert u.reg_read(ar.UC_ARM_REG_PC)==0x20000000
  for r,v in saved.items():u.reg_write(r,v)
 phase='resume';u.emu_start(resume|1,0x20000000,count=1000);assert u.reg_read(ar.UC_ARM_REG_PC)==0x20000000
 newbytes=bytes(u.mem_read(NEW,32));return dict(partial_descriptor=partial,final_descriptor=list(struct.unpack('<III',u.mem_read(CTX+56,12))),new_buffer=newbytes.hex(),guard_bytes_changed=sum(v!=0xcc for v in newbytes[2:]),old_buffer=u.mem_read(OLD,32).hex(),trace=trace,sp=u.reg_read(ar.UC_ARM_REG_SP),primask=u.reg_read(ar.UC_ARM_REG_PRIMASK))
results=[]
for inject in [False,True]:
 x=run(False,inject);y=run(True,inject);assert x==y;assert y['guard_bytes_changed']==(6 if inject else 0);assert y['final_descriptor']==([NEW+8,2,0] if inject else [NEW,2,0]);results.append(dict(injected=inject,result=y))
r=dict(status='PASS_CONTROLLED_DESCRIPTOR_INTERLEAVING',elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),comparisons=results,limits=['Manually invoke IRQ function between pointer and size stores in the same guest RAM, then restore setter registers and resume. This is not a physical exception/preemption trace.','Both actual stock and public API/IRQ/helpers execute; no semantic helper stubs.','Model a future unprotected thread-side buffer swap: old16-element descriptor replaced with a2-element buffer. Existing stock initializer and event callback use static16-element buffers; no claim this corruption occurs in stock hardware.','Serialization must be supplied by caller, as public SDK documents. IRQ enabled/pending/priority, exception stacking, real FIFO timing and allocator lifetime not proven.'])
(D/'interleave-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS control and injected stock/public interleaving; six guard bytes change only in injected case')
