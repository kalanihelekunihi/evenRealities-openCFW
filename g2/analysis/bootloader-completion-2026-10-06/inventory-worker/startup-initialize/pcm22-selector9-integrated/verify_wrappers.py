from pathlib import Path
import json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
import unicorn.arm_const as a
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
elf=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/build/bootloader-completion/pcm22-selector9-integrated/7ffc7b0eafdf7e6fd13eaaeaacac1c1ea3826f7f1f32d52d73604d17ae84e651/candidate.elf');segments=[];sy={}
with elf.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((int(s['p_vaddr']),s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():sy[s.name]=int(s['st_value'])
visited={'power':set(),'boost':set()}
def run(stock,kind,present,x,y,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for addr,size in [(0x10000,0x10000),(0x30000,0x10000),(0x50000,0x10000),(0x410000,0x30000),(0x20000000,0x40000),(0x8000000,0x1000)]:u.mem_map(addr,size)
 if stock:u.mem_write(0x410000,blob)
 else:
  for addr,data in segments:u.mem_write(addr,data)
 def w(addr,v):u.mem_write(addr,struct.pack('<I',v))
 ptr=0x20026e3c if kind=='power' else 0x20026e64;w(ptr,0x8000101 if present else 0)
 u.mem_write(0x20002000,b'\x02');u.reg_write(a.UC_ARM_REG_R0,x);u.reg_write(a.UC_ARM_REG_R1,y);u.reg_write(a.UC_ARM_REG_R2,0x20002000)
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xabc000+i)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_PRIMASK,mask);events=[]
 def hook(cpu,pc,size,data):
  if pc==0x8000000:cpu.emu_stop();return
  if pc==0x8000100:
   events.append([cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(3)] if kind=='power' else [])
   if kind=='power':cpu.mem_write(0x20002000,b'\x07')
   cpu.reg_write(a.UC_ARM_REG_R0,0x55aa);cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if stock:visited[kind].update(range(pc,pc+size))
 u.hook_add(UC_HOOK_CODE,hook)
 entry=(0x41cd1a if kind=='power' else 0x41cdb8) if stock else sy['power_state_wrapper' if kind=='power' else 'boost_service_wrapper']
 u.emu_start(entry|1,0,count=1000)
 assert u.reg_read(a.UC_ARM_REG_PC)==0x8000000
 return dict(events=events,state=bytes(u.mem_read(0x20002000,1)).hex(),result=u.reg_read(a.UC_ARM_REG_R0) if kind=='power' else None,callee_saved=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],sp=u.reg_read(a.UC_ARM_REG_SP),primask=u.reg_read(a.UC_ARM_REG_PRIMASK))
rows=[]
for kind,present,x,y,mask in itertools.product(['power','boost'],[0,1],[0,1,0x1234,0xffffffff],[0,1,0x1234,0xffffffff],[0,1]):
 original=run(True,kind,present,x,y,mask);source=run(False,kind,present,x,y,mask);assert original==source,(kind,present,x,y,original,source);rows.append(dict(kind=kind,callback_present=present,stimulus=x,on=y,mask=mask,result=source))
out=dict(status='PASS',cases=len(rows),blob_sha256=hashlib.sha256(blob).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),source_sha256=hashlib.sha256((HERE/'spot_sleep_wrappers.c').read_bytes()).hexdigest(),coverage={k:len(v) for k,v in visited.items()},results=rows,limits=['Callback implementation is a stub recording args, writing synthetic state7 and returning55aa; this proves dispatch/ABI only.','Boost wrapper is void per upstream and caller; original R0 is restored caller R7, not callback result, and is excluded for this void interface.','No hardware, sleep timing or concurrency proof.'])
(HERE/'wrappers-comparison.json').write_text(json.dumps(out,indent=2));print('PASS',len(rows),out['coverage'])
