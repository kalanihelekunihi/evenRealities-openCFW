from pathlib import Path
import struct,json,itertools,hashlib,argparse
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn import arm_const as a
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-task-delay.elf'));args=ap.parse_args()
with args.elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
children=[('guard',0x41602a),('mask',0x41b2f8),('suspend',0x4181d8),('block',0x419186),('resume',0x418228),('reschedule',0x41b3d0)];visited=set();SP=0x2003f000

def run(stock,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for p,n in [(0x410000,0x30000),(0x70000,0x10000),(0x8000000,0x1000),(0x20000000,0x40000),(0xfffff000,4096)]:u.mem_map(p,n)
 if stock:u.mem_write(0x410000,blob)
 else:
  for p,data in segments:u.mem_write(p,data)
 for i in range(6):u.mem_write(0x8000100+16*i,b'\x70\x47')
 u.mem_write(0x2002716c,struct.pack('<I',f['suspended']));u.reg_write(a.UC_ARM_REG_R0,f['ticks']);u.reg_write(a.UC_ARM_REG_SP,SP);u.reg_write(a.UC_ARM_REG_LR,0x8000001)
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xaac000+i)
 events=[];terminal=[];done=[False]
 def hook(cpu,pc,size,_):
  if pc==0x8000000:done[0]=True;u.emu_stop();return
  if stock and any(lo<=pc<hi for lo,hi in [(0x416378,0x41639a),(0x417fa8,0x417fe4)]):visited.update(range(pc,pc+size))
  for i,(name,original) in enumerate(children):
   if pc!=(original if stock else 0x8000100+16*i):continue
   r0=cpu.reg_read(a.UC_ARM_REG_R0);r1=cpu.reg_read(a.UC_ARM_REG_R1);events.append([name,*([r0,r1] if name=='block' else [])]);value=f['guard'] if name=='guard' else f['resume'] if name=='resume' else 0
   if name=='mask':cpu.reg_write(a.UC_ARM_REG_BASEPRI,48)
   if name=='suspend':u.mem_write(0x2002716c,struct.pack('<I',f['suspended']+1))
   if name=='resume':u.mem_write(0x2002716c,struct.pack('<I',f['suspended']))
   cpu.reg_write(a.UC_ARM_REG_R0,value)
   if stock:cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR))
   return
  if not stock:assert not 0x410000<=pc<0x435000
 def store(cpu,access,p,size,value,_):
  if p==0xffffffff:terminal.append(['assert-fault-write',p,size,value,cpu.reg_read(a.UC_ARM_REG_BASEPRI)]);done[0]=True;u.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,store);entry=(0x416378 if f['entry']=='cmsis' else 0x417fa8) if stock else sy['opencfw_cmsis_delay' if f['entry']=='cmsis' else 'opencfw_kernel_delay'];
 try:u.emu_start(entry|1,0,count=5000)
 except UcError:
  if not terminal:raise
 assert done[0]
 if terminal:return {'events':events,'terminal':terminal}
 return {'events':events,'return':u.reg_read(a.UC_ARM_REG_R0) if f['entry']=='cmsis' else None,'terminal':terminal,'sp':u.reg_read(a.UC_ARM_REG_SP),'saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],'basepri':u.reg_read(a.UC_ARM_REG_BASEPRI),'suspended':struct.unpack('<I',u.mem_read(0x2002716c,4))[0]}
rows=[]
for entry,ticks,suspended,resume,guard in itertools.product(['cmsis','kernel'],[0,1,2,0x80000000,0xffffffff],[0,1,0xffffffff],[0,1,7],[0,1,0x80]):
 f=dict(entry=entry,ticks=ticks,suspended=suspended,resume=resume,guard=guard);x=run(True,f);y=run(False,f)
 if x!=y:(N/'failure.json').write_text(json.dumps({'fixture':f,'stock':x,'source':y},indent=2));raise AssertionError((f,x,y))
 rows.append({'fixture':f,'result':x})
r={'status':'PASS_TASK_DELAY_BODIES_WITH_SCHEDULER_CONTRACTS','cases':len(rows),'original_sha256':hashlib.sha256(blob).hexdigest(),'source_sha256':hashlib.sha256((N/'task_delay.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'bodies':[{'start':hex(lo),'end':hex(hi),'bytes':hi-lo,'visited':len(set(range(lo,hi))&visited)} for lo,hi in [(0x416378,0x41639a),(0x417fa8,0x417fe4)]],'comparisons':rows,'limits':['Guard and scheduler children are controlled returns/effects; their existing native implementations are not exercised by this body corpus. No live task scheduling or tick duration claim.','Kernel delay has void ABI; undefined returnR0 is excluded. CMSIS status, callee-saved registers,SP,BASEPRI, scheduler state and ordered helperargs compare.','Scheduler-suspended positive delay enters the real invalid-address store path; test stops at its pre-write hook. No hardware/host invalid-address store occurs.']};(N/'comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'],r['bodies'])
