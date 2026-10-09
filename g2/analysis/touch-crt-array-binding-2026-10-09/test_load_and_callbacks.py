from pathlib import Path
import json,struct,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
O=Path(__file__).resolve().parent;R=O.parents[2];fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';blob=fw.read_bytes();assert hashlib.sha256(blob).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=blob[32:];w=lambda a:struct.unpack_from('<I',b,a-0x3300)[0]
copy_start=w(0x46e8);copy_end=w(0x46ec);zero_start=w(0x46f0);zero_end=w(0x46f4)
copy=[{'table':hex(a),'source':w(a),'destination':w(a+4),'words':w(a+8)} for a in range(copy_start,copy_end,12)]
zero=[{'table':hex(a),'destination':w(a),'words':w(a+4)} for a in range(zero_start,zero_end,8)]
assert copy==[{'table':'0xb578','source':0xb58c,'destination':0x200004c0,'words':241}]
assert zero==[{'table':'0xb584','destination':0x200008a8,'words':428}]
inputs=[fw,O/'outputs/linked.elf',R/'g2/analysis/touch-startup-provider-successor-2026-10-09/outputs/linked.elf',R/'g2/analysis/touch-newlib14-startup-exit-2026-10-09/outputs/exit/linked.elf'];overlays=[]
for p in inputs[1:]:
 with p.open('rb') as f:
  for s in ELFFile(f).iter_sections():
   if s.name.startswith('.text') or s.name in ['.init','.fini']:overlays.append((s['sh_addr'],s.data()))
regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def run(pattern,seed,native,manual_fini):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0,0x20000);u.mem_write(0x3300,b);u.mem_map(0x20000000,0x2000);u.mem_write(0x20000000,bytes([pattern])*0x2000);u.mem_map(0xe000e000,0x1000)
 if native:
  for a,d in overlays:u.mem_write(a,d)
 sp=0x20001f00;u.reg_write(UC_ARM_REG_SP,sp);phase='';events=[];writes=[];stopped=[];halts=0
 def hook(uc,a,size,data):
  nonlocal halts
  if phase=='load' and a==0x46d6:stopped.append('before-reset-c-call');uc.emu_stop()
  elif a==0x2000:stopped.append('return');uc.emu_stop()
  elif a in [0xaa44,0x3434,0x33e0,0x3408,0x33c0]:events.append({'phase':phase,'entry':hex(a)})
  elif a==0xaa40:
   halts+=1
   if halts==1:events.append({'phase':phase,'entry':hex(a),'status':uc.reg_read(UC_ARM_REG_R0)})
   if halts==5:stopped.append('four-halt-branches');uc.emu_stop()
 def write(uc,access,a,size,value,data):
  if phase=='load':writes.append((a,size,value))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
 phase='load';u.emu_start(0x467f,0,count=20000);assert stopped==['before-reset-c-call']
 assert bytes(u.mem_read(0x20000400,192))==b[:192]
 assert bytes(u.mem_read(0x200004c0,964))==b[0xb58c-0x3300:0xb950-0x3300]
 assert bytes(u.mem_read(0x200008a8,1712))==bytes(1712)
 assert int.from_bytes(u.mem_read(0xe000ed08,4),'little')==0x20000400
 assert int.from_bytes(u.mem_read(0x2000087c,4),'little')==0x3435
 assert int.from_bytes(u.mem_read(0x20000880,4),'little')==0x3409
 assert bytes(u.mem_read(0x20000884,36))==bytes([pattern])*36
 load={'copy_word_writes':sum(a>=0x200004c0 and a<0x20000884 for a,s,v in writes),'zero_word_writes':sum(a>=0x200008a8 and a<0x20000f58 for a,s,v in writes),'vtor':hex(int.from_bytes(u.mem_read(0xe000ed08,4),'little')),'init':hex(int.from_bytes(u.mem_read(0x2000087c,4),'little')),'fini':hex(int.from_bytes(u.mem_read(0x20000880,4),'little'))}
 values=[(0x2468ace0+seed+i*0x01010101)&0xffffffff for i in range(8)]
 def invoke(a,label):
  nonlocal phase
  phase=label;stopped.clear();u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x2001)
  for r,v in zip(regs,values):u.reg_write(r,v)
  u.emu_start(a|1,0,count=1000);assert stopped
  if label!='exit':assert [u.reg_read(x) for x in regs]==values and u.reg_read(UC_ARM_REG_SP)==sp
 invoke(0xa9e4,'constructor');assert [x['entry'] for x in events]==['0xaa44','0x3434','0x33e0'];assert u.mem_read(0x200008a8,1)==bytes([0])
 if manual_fini:
  invoke(0x3408,'manual-fini-first');assert u.mem_read(0x200008a8,1)==bytes([1]);invoke(0x3408,'manual-fini-second')
  assert [x['entry'] for x in events[3:]]==['0x3408','0x33c0','0x3408']
 before=int.from_bytes(u.mem_read(0x200008a8,1),'little');u.reg_write(UC_ARM_REG_R0,seed);invoke(0xa9ac,'exit');assert stopped==['four-halt-branches'];assert int.from_bytes(u.mem_read(0x200008a8,1),'little')==before
 assert events[-1]=={'phase':'exit','entry':'0xaa40','status':seed}
 return {'load':load,'events':events,'completed_after':before,'stdio_handler':int.from_bytes(u.mem_read(0x20000f54,4),'little'),'ram_sha256':hashlib.sha256(bytes(u.mem_read(0x20000000,0x2000))).hexdigest()}
rows=[]
for pattern,seed,manual in itertools.product([0,0x55,0xa5,0xff],range(4),[0,1]):
 a=run(pattern,seed,False,manual);c=run(pattern,seed,True,manual);assert a==c;rows.append({'pattern':pattern,'seed':seed,'manual_fini':manual,'matches':True,'observed':a})
result={'status':'PASS','cases':len(rows),'vector_reset':hex(w(0x3304)),'copy_tables':copy,'zero_tables':zero,'comparisons':rows,'inputs':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'limits':'Actual stock copy/zero loop and actual image callbacks, source-produced constructor/CRT and binary-attributed crtbegin provider. Starts after hardware/system initialization at467E, stops before reset C call, then explicitly invokes constructor. Simulated VTOR register backing, not NVIC delivery. Manual finalizer invocation is labeled and is not exit reachability. No full reset/application run or live device state.'}
(O/'original-results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(rows));print(json.dumps({'copy':copy,'zero':zero},indent=2))
