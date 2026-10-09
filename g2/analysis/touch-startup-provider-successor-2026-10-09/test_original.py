"""Original/rebuilt instruction pairs with explicit synthetic callback backing."""
from pathlib import Path
import json,hashlib,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
O=Path(__file__).resolve().parent;R=O.parents[2];fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';blob=fw.read_bytes();assert hashlib.sha256(blob).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
sections=[]
with (O/'outputs/linked.elf').open('rb') as f:
 for s in ELFFile(f).iter_sections():
  if s.name in ['.text','.init','.fini']:sections.append((s['sh_addr'],s.data()))
exitelf=R/'g2/analysis/touch-newlib14-startup-exit-2026-10-09/outputs/exit/linked.elf'
with exitelf.open('rb') as f:s=ELFFile(f).get_section_by_name('.text');sections.append((s['sh_addr'],s.data()))
with (O/'halt-output-attempt2/default-halt.o').open('rb') as f:s=ELFFile(f).get_section_by_name('.text._exit');sections.append((0xaa40,s.data()))
registers=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def run(entry,seed,native,status=0,handler=0):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0,0x20000);u.mem_map(0x20000000,0x20000);u.mem_write(0x3300,blob[32:])
 if native:
  for a,d in sections:u.mem_write(a,d)
 callback=0x20001000;u.mem_write(callback,bytes([seed&255,0x20,0x70,0x47]));u.mem_write(0x2000087c,struct.pack('<I',callback|1));u.mem_write(0x20000f54,struct.pack('<I',callback|1 if handler else 0))
 values=[(0x13579bdf+seed+i*0x01010101)&0xffffffff for i in range(8)]
 for reg,v in zip(registers,values):u.reg_write(reg,v)
 sp=0x2001e000;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x2001);u.reg_write(UC_ARM_REG_R0,status&0xffffffff);events=[];stop=[];loops=0
 def hook(uc,a,size,data):
  nonlocal loops
  if a==0x2000:stop.append('return');uc.emu_stop()
  elif a==callback:events.append({'callback':hex(callback),'r0':uc.reg_read(UC_ARM_REG_R0)})
  elif a==0xaa44:events.append({'provider':'_init'})
  elif a==0xaa40:
   loops+=1
   if loops==1:events.append({'provider':'_exit','status':uc.reg_read(UC_ARM_REG_R0)})
   if loops==5:stop.append('four-halt-branches');uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(entry|1,0,count=1000);assert stop
 regs=[u.reg_read(x) for x in registers]
 if entry in [0xa9e4,0xaa44,0xaa50]:assert regs==values and u.reg_read(UC_ARM_REG_SP)==sp
 if entry==0xa9e4:assert [x.get('provider','callback') for x in events]==['_init','callback']
 if entry==0xa9ac:assert events[-1]=={'provider':'_exit','status':status&0xffffffff} and len(events)==1+handler
 return {'events':events,'stop':stop,'callee_saved':regs,'sp':u.reg_read(UC_ARM_REG_SP),'r0':u.reg_read(UC_ARM_REG_R0),'stack_bytes':bytes(u.mem_read(sp-64,64)).hex()}
rows=[]
for entry in [0xa9e4,0xaa44,0xaa50]:
 for seed in range(8):
  a=run(entry,seed,False);b=run(entry,seed,True);assert a==b;rows.append({'entry':hex(entry),'seed':seed,'matches':True,'observed':a})
for status in [0,1,-1,0x80000000]:
 for handler in [0,1]:
  for seed in range(4):
   a=run(0xa9ac,seed,False,status,handler);b=run(0xa9ac,seed,True,status,handler);assert a==b;rows.append({'entry':'0xa9ac','seed':seed,'status':status,'handler':handler,'matches':True,'observed':a})
result={'status':'PASS','cases':len(rows),'comparisons':rows,'native_halt':'genuine default libnosys source-built4bytes now overlaid, unlike preliminary run using stock halt','inputs':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [fw,O/'outputs/linked.elf',exitelf,O/'halt-output-attempt2/default-halt.o']},'limits':'Real stock/rebuilt instructions and exact linker bounds. One synthetic init-array callback and optional stdio callback are simple supplied RAM instructions; no actual runtime callback contents, startup reachability, scheduling, hardware or full program cleanup proved. Real halt branch executes four times; no divide instruction executes. Registers/SP/stack side effects compared.'}
(O/'original-results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(rows))
