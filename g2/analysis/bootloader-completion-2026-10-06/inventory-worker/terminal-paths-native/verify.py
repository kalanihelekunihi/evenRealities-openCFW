from pathlib import Path
import hashlib,json,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn import arm_const as a
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with Path('/tmp/opencfw-terminal-paths.elf').open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
entries={'task':('opencfw_task_return_native',0x41b390,0x41b3ba),'malloc':('opencfw_malloc_failed_native',0x41b5f6,0x41b600),'overflow':('opencfw_stack_overflow_native',0x41b600,0x41b60c),'dfu':('opencfw_dfu_terminal_native',0x42e1da,0x42e1ec),'platform':('opencfw_platform_terminal_native',0x4329c4,0x4329d2)};children=[('signal',0x42e444),('delay',0x416378),('print',0x415fae),('mask',0x41b2f8),('exit',0x41b298)];visited=set();SP=0x2003f000

def run(stock,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for p,n in [(0x410000,0x30000),(0x70000,0x10000),(0x8000000,4096),(0x20000000,0x40000),(0xfffff000,4096)]:u.mem_map(p,n)
 if stock:u.mem_write(0x410000,blob)
 else:
  for p,data in segs:u.mem_write(p,data)
 for i in range(5):u.mem_write(0x8000100+16*i,b'\x70\x47')
 u.mem_write(0x200004c4,struct.pack('<I',f['critical']));u.mem_write(0x20001000,b'worker-test\0');u.reg_write(a.UC_ARM_REG_SP,SP);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_R0,f['status']);u.reg_write(a.UC_ARM_REG_R1,0x20001000)
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xaac000+i)
 events=[];done=[False];terminal=[];repeats={};loads=[0]
 def string(p):
  x=bytearray()
  while u.mem_read(p,1)[0]:x+=u.mem_read(p,1);p+=1
  return bytes(x).hex()
 def code(cpu,pc,size,_):
  if pc==0x8000000:done[0]=True;terminal.append(['debug-return',cpu.reg_read(a.UC_ARM_REG_R0),cpu.reg_read(a.UC_ARM_REG_SP),*[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)]]);u.emu_stop();return
  if bytes(u.mem_read(pc,2))==b'\x00\xbe':terminal.append(['stock-breakpoint0']);done[0]=True;u.emu_stop();return
  if stock and any(lo<=pc<hi for _,lo,hi in entries.values()):visited.update(range(pc,pc+size))
  for i,(name,orig) in enumerate(children):
   if pc!=(orig if stock else 0x8000100+16*i):continue
   r0=cpu.reg_read(a.UC_ARM_REG_R0);r1=cpu.reg_read(a.UC_ARM_REG_R1)
   if name=='print':events.append(['print',string(r0),string(r1) if f['entry']=='overflow' else None])
   elif name=='mask':events.append(['mask']);cpu.reg_write(a.UC_ARM_REG_BASEPRI,48)
   else:events.append([name,r0])
   if name in ['delay','exit'] and sum(e[0]==name for e in events)==2:terminal.append(['two-'+name+'-requests']);done[0]=True;u.emu_stop();return
   cpu.reg_write(a.UC_ARM_REG_R0,f['child_return'])
   if stock:cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR))
   return
  if f['entry']=='malloc' and events:
   repeats[pc]=repeats.get(pc,0)+1
   if repeats[pc]==4:terminal.append(['spin-after-print']);done[0]=True;u.emu_stop()
  if not stock:assert not 0x410000<=pc<0x435000
 def mem(cpu,access,p,size,value,_):
  if access==UC_MEM_WRITE and p==0xffffffff:terminal.append(['invalid-store',p,size,value,cpu.reg_read(a.UC_ARM_REG_BASEPRI)]);done[0]=True;u.emu_stop()
  if access==UC_MEM_READ and p==SP-8 and f['entry']=='task' and f['critical']==0xffffffff:
   loads[0]+=1
   if loads[0]==3:u.mem_write(p,struct.pack('<I',f['release']))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,mem);u.hook_add(UC_HOOK_MEM_READ,mem);entry=entries[f['entry']][1] if stock else sy[entries[f['entry']][0]]
 try:u.emu_start(entry|1,0,count=5000)
 except UcError:
  if not done[0]:raise
 assert done[0],(stock,f,hex(u.reg_read(a.UC_ARM_REG_PC)))
 return {'events':events,'terminal':terminal,'basepri':u.reg_read(a.UC_ARM_REG_BASEPRI)}
rows=[]
for entry,critical,status,child,release in itertools.product(entries,[0,0xffffffff],[0,0xdeadbeef],[0,0xfffffffa],[1,123,0xffffffff]):
 f={'entry':entry,'critical':critical,'status':status,'child_return':child,'release':release};x=run(True,f);y=run(False,f)
 if x!=y:(N/'failure.json').write_text(json.dumps({'fixture':f,'stock':x,'source':y},indent=2));raise AssertionError((f,x,y))
 rows.append({'fixture':f,'result':x})
r={'status':'PASS_FIVE_TERMINAL_PATHS_WITH_DECLARED_CHILDREN','cases':len(rows),'original_sha256':hashlib.sha256(blob).hexdigest(),'source_sha256':hashlib.sha256((N/'terminal_paths.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(Path('/tmp/opencfw-terminal-paths.elf').read_bytes()).hexdigest(),'original_bodies':[{'name':name,'start':lo,'end':hi,'bytes':hi-lo,'visited':len(visited&set(range(lo,hi)))} for name,(_,lo,hi) in entries.items()],'comparisons':rows,'limits':['Child print/mask/signal/delay/exit effects are declared synthetic contracts; source/stock body instructions execute independently.','Debugger release is a synthetic write to the exact original/native SP-8 slot. Invalid store, BKPT0 and recurring loops are stopped by the offline harness; no hardware fault/exit/debugger event is asserted.','Noreturn paths compare diagnostic bytes, name argument, ordered requests and stopping boundary, not incidental stack/register layout. Debug-return path compares rawR0,SP,R4-R11 and mask.']};(N/'comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'],r['original_bodies'])
