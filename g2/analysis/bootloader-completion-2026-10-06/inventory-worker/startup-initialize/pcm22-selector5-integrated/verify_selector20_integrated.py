from pathlib import Path
import json,struct,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import *
import unicorn.arm_const as a
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists());c=json.loads((HERE/'current-candidate.json').read_text());base=ROOT/c['directory']/'candidate.elf';addon=Path('/tmp/opencfw-pcm22-selector6.elf');blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
segments=[];sy={}
for f in [base]:
 with f.open('rb') as handle:
  e=ELFFile(handle)
  for s in e.iter_segments():
   if s['p_type']=='PT_LOAD':segments.append((int(s['p_vaddr']),s.data()))
  sy.update({s.name:int(s['st_value']) for s in e.get_section_by_name('.symtab').iter_symbols()})
visited=set()
def run(stock,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for addr,size in [(0,0x1000),(0x10000,0x10000),(0x30000,0x10000),(0x50000,0x10000),(0x410000,0x30000),(0x20000000,0x40000),(0x40000000,0x300000),(0x47ff0000,0x1000),(0xe000e000,0x2000),(0x8000000,0x20000)]:u.mem_map(addr,size)
 if stock:u.mem_write(0x410000,blob)
 else:
  for addr,data in segments:u.mem_write(addr,data)
 def w(addr,value):u.mem_write(addr,struct.pack('<I',value&0xffffffff))
 for i in range(20):w(0x20026ba4+4*i,((0x45+i)&127)|(((0x101+7*i)&1023)<<7)|((i&15)<<17)|(((0x22+i)&127)<<21))
 for addr,value in [(0x20026c04,0x0dabc123),(0x20026bf4,0x00123456),(0x20026bf8,0x000fedcb),(0x20026bfc,0x000abcde),(0x20026c00,0x00013579),(0x40020344,0x01020304),(0x40020354,0x00543210),(0x40020358,0x87654321),(0x40020044,0xaabbccdd),(0x4002004c,0x11223344),(0x40020080,0x55667788),(0x200270b0,0x39),(0x200270b4,0x45),(0x200270b8,0x123),(0x200270bc,4),(0x40021000,5),(0x40004030,0x1000000),(0x40004044,0x20),(0x400083e0,f['timer']),(0x40008010,0xffffffff)]:w(addr,value)
 u.mem_write(0x2000055a,bytes([f['service_state']]));u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_PRIMASK,f['mask']);writes=[];done=[False];rom=[];delay_count=0
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xabc000+i)
 for i,key in enumerate(['target','current','ton','old_ton']):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),f[key])
 def code(cpu,pc,size,data):
  nonlocal delay_count
  if pc==0x8000000:done[0]=True;cpu.emu_stop();return
  if pc==0x40:rom.append(cpu.reg_read(a.UC_ARM_REG_R0));delay_count+=1;cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if not stock and 0x410000<=pc<0x435000:raise AssertionError(('locked code on source',hex(pc)))
  if stock and 0x429b4c<=pc<0x429c46:visited.update(range(pc,pc+size))
 def write(cpu,access,addr,size,value,data):
  if 0x40000000<=addr<0x40300000 or 0xe000e000<=addr<0xe0020000 or 0x20027000<=addr<0x20027200:writes.append([addr,size,value&((1<<(size*8))-1)])
 def read(cpu,access,addr,size,value,data):
  if addr==0x40008064:w(addr,0x40000000 if delay_count>=f["ready_after"] else 0)
 u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((0x429b4c if stock else sy['opencfw_spot_pcm22_transition20'])|1,0,count=200000);assert done[0],hex(u.reg_read(a.UC_ARM_REG_PC))
 return dict(result=u.reg_read(a.UC_ARM_REG_R0),mask=u.reg_read(a.UC_ARM_REG_PRIMASK),sp=u.reg_read(a.UC_ARM_REG_SP),writes=writes,rom_delay_inputs=rom,callee_saved=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)])
rows=[]
for timer,ready,state,mask,target,current,ton in itertools.product([0,1],[0,2,60,100],[26,2,7],[0,1],[5,1],[13],[0,6]):
 f=dict(timer=timer,ready_after=ready,service_state=state,mask=mask,target=target,current=current,ton=ton,old_ton=7);x=run(True,f);y=run(False,f)
 if x!=y:(HERE/'selector20-failure.json').write_text(json.dumps(dict(fixture=f,stock=x,source=y),indent=2));raise AssertionError((f,x,y))
 rows.append(dict(fixture=f,result=x))
out=dict(status='PASS',cases=len(rows),base_elf_sha256=c['sha256'],original_body_sha256=hashlib.sha256(blob[0x19b4c:0x19c46]).hexdigest(),covered_body_bytes=len(visited),results=rows,limits=['Clock/timer/SCS accesses are synthetic registers; no peripheral W1C or concurrency proof.','Integrated image executes native delay/timer-service and downstream2b/7b source providers from217-object image; only unavailable resident ROM delay40 is stubbed with recorded inputs. No source-side locked instruction execution.','Ready-after delay counts are synthetic MMIO stimuli, not observed IRQ scheduling or physical time.'])
(HERE/'selector20-comparison.json').write_text(json.dumps(out,indent=2));print('PASS',len(rows),len(visited),'original body bytes')
