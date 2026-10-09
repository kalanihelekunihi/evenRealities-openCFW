from pathlib import Path
import sys,struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;P=D.parent/'audio-uart-tx-ownership-2026-10-09';sys.path.insert(0,str(P));import verify as v
STATE=0x2006a380;DESC=0x20000d80;QBUF=0x200ba420;BASE=0x4003c000
def run(f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,v.raw);u.mem_map(0x100000,0x10000)
 for a,b in v.sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0x40039000,0x4000)
 def w(a,x):u.mem_write(a,struct.pack('<I',x))
 w(STATE,0x1ea9e06);w(STATE+0x28,3);w(DESC+4,STATE);u.mem_write(DESC+24,b'\1\0')
 data=bytes(0x40+i for i in range(f['length']));u.mem_write(QBUF,data+bytes(1024-len(data)))
 w(STATE+0x34,f['length']);w(STATE+0x38,0);w(STATE+0x3c,f['length']);w(STATE+0x40,1024);w(STATE+0x44,1);w(STATE+0x48,QBUF);u.mem_write(STATE+0xdc,b'\1');u.mem_write(STATE+0x119,b'\0')
 w(BASE+0x40,f['status']);w(BASE+0x18,0x20 if f['budget']==0 else 0);remaining=[f['budget']];fifo=[];done=[]
 u.reg_write(UC_ARM_REG_R0,3);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01)
 def mem(uc,access,a,size,value,user):
  if a==BASE:
   fifo.append(value&255);remaining[0]-=1
   if remaining[0]==0:w(BASE+0x18,0x20)
 def hook(uc,pc,n,user):
  if native and pc==0x58e534:uc.reg_write(UC_ARM_REG_PC,v.syms['nonblocking_write_sm']|1);return
  if pc==0x10ff00:done.append(1);uc.emu_stop();return
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,mem);u.emu_start(0x55e2cf,0,count=100000);assert done
 return {'fifo':fifo,'queue':list(struct.unpack('<6I',u.mem_read(STATE+0x34,24))),'queue_bytes':bytes(u.mem_read(QBUF,max(1,f['length']))).hex(),'completion':u.mem_read(DESC+25,1)[0],'last_tx_complete':u.mem_read(STATE+0xde,1)[0],'interrupt_clear':int.from_bytes(u.mem_read(BASE+0x44,4),'little')}
rows=[];diff=[]
for length,budget,status in itertools.product([0,1,3,8,32],[0,1,2,1000],[0x20,0x21]):
 f={'length':length,'budget':budget,'status':status};a=run(f,False);b=run(f,True);rows.append({'fixture':f,'observed':a,'matches':a==b})
 if a!=b:diff.append({'fixture':f,'stock':a,'source':b})
out={'status':'PASS' if not diff else 'DIFFERENCES','cases':len(rows),'elf_sha256':hashlib.sha256(v.elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(v.raw).hexdigest(),'comparisons':rows,'differences':diff,'limits':'Direct channel3 common IRQ entry with synthetic status/FIFO readiness. Original HAL interrupt service and original/native TX state machine/queue drain. No vector/NVIC delivery or physical transmission.'}
(D/'results.json').write_text(json.dumps(out,indent=2)+'\n');print('CASES',len(rows),'DIFFERENCES',len(diff))
