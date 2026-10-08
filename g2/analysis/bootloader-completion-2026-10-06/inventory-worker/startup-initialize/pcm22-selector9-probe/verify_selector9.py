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
visited={9:set()};extents={9:(0x428ca4,0x428d90)}
def run(stock,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for addr,size in [(0,0x1000),(0x10000,0x10000),(0x30000,0x10000),(0x50000,0x10000),(0x410000,0x30000),(0x20000000,0x40000),(0x40000000,0x300000),(0x47ff0000,0x1000),(0xe000e000,0x2000),(0xe001e000,0x1000),(0x8000000,0x20000)]:u.mem_map(addr,size)
 if stock:u.mem_write(0x410000,blob)
 else:
  for addr,data in segments:u.mem_write(addr,data)
 def w(addr,value):u.mem_write(addr,struct.pack('<I',value&0xffffffff))
 for i in range(20):w(0x20026ba4+4*i,((0x45+i)&127)|(((0x101+7*i)&1023)<<7)|((i&15)<<17)|(((0x22+i)&127)<<21))
 for addr,value in [(0x20026c04,0x0dabc123),(0x20026bf4,0x00123456),(0x20026bf8,0x000fedcb),(0x20026bfc,0x000abcde),(0x20026c00,0x00013579),(0x40020344,0x01020304),(0x40020354,0x00543210),(0x40020358,0x87654321),(0x40020044,0xaabbccdd),(0x4002004c,0x11223344),(0x40020080,0x55667788),(0x200270b0,0x39),(0x200270b4,0x45),(0x200270b8,0x123),(0x200270bc,4),(0x40021000,0xa5000000),(0x40004030,0),(0x40004044,f['enable']),(0x20000154,f['last']),(0x4002037c,0x876543ff),(0x400083e0,f['timer']),(0x40008010,0xffffffff)]:w(addr,value)
 for key,index in [('new_trim',f['target']),('old_trim',f['current'])]:
  addr=0x20026ba4+4*index;v=struct.unpack('<I',u.mem_read(addr,4))[0];w(addr,(v&~(127<<21))|(f[key]<<21))
 w(0xe000ed14,f['cache_enabled']<<17);w(0xe001e300,f.get('cache_block',0))
 u.mem_write(0x2000055a,bytes([f['service_state']]));u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_PRIMASK,f['mask']);writes=[];done=[False];rom=[];delay_count=0;switch_reads=0;hp_reads=0;timer_reads=0
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xabc000+i)
 for i,key in enumerate(['target','current','ton','old_ton']):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),f[key])
 def code(cpu,pc,size,data):
  nonlocal delay_count
  if pc==0x8000000:done[0]=True;cpu.emu_stop();return
  if pc==0x40:rom.append(cpu.reg_read(a.UC_ARM_REG_R0));delay_count+=1;cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if not stock and 0x410000<=pc<0x435000:raise AssertionError(('locked code on source',hex(pc)))
  if stock and extents[f['selector']][0]<=pc<extents[f['selector']][1]:visited[f['selector']].update(range(pc,pc+size))
 def write(cpu,access,addr,size,value,data):
  if 0x40000000<=addr<0x40300000 or 0xe000e000<=addr<0xe0020000 or 0x20027000<=addr<0x20027200 or addr in [0x2000055a,0x20000154]:writes.append([addr,size,value&((1<<(size*8))-1)])
 def read(cpu,access,addr,size,value,data):
  nonlocal switch_reads,hp_reads,timer_reads
  if addr==0x40008064:w(addr,0x40000000 if delay_count>=f["ready_after"] else 0)
  if addr==0x40021000:
   v=struct.unpack('<I',cpu.mem_read(addr,4))[0];switch_reads+=1;w(addr,(v&~4)|(4 if switch_reads>=f['switch_after'] else 0))
  if addr==0x40004030:
   hp_reads+=1;w(addr,0x01000000 if hp_reads>=f['hp_after'] else 0)
  if addr==0x400083e0:
   timer_reads+=1
   if f.get('timer_drop') and timer_reads>1:w(addr,0)
 u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((extents[f['selector']][0] if stock else sy['opencfw_spot_pcm22_transition'+str(f['selector'])])|1,0,count=200000);assert done[0],hex(u.reg_read(a.UC_ARM_REG_PC))
 return dict(result=u.reg_read(a.UC_ARM_REG_R0),mask=u.reg_read(a.UC_ARM_REG_PRIMASK),sp=u.reg_read(a.UC_ARM_REG_SP),writes=writes,rom_delay_inputs=rom,callee_saved=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)])
rows=[]
fixtures=[]
for timer,ready,state,ton,mask in itertools.product([0,1],[0,2,60,100],[26,2,7],[0,6],[0,1]):
 fixtures.append(dict(selector=9,timer=timer,ready_after=ready,last=99,enable=32,hp_after=1,switch_after=1,service_state=state,mask=mask,target=0,current=8,ton=ton,old_ton=7,new_trim=70,old_trim=40,cache_enabled=0))
for old,new in itertools.product([0,1,40,63,64,100,127],[0,1,40,63,64,100,127]):fixtures.append(dict(fixtures[0],old_trim=old,new_trim=new))
for target,timer,ready,state,ton,mask in itertools.product([8,12],[0,1],[0,100],[26,2,7],[0,6],[0,1]):fixtures.append(dict(fixtures[0],target=target,current=12 if target==8 else 8,timer=timer,ready_after=ready,service_state=state,ton=ton,mask=mask))
for f in fixtures:
 x=run(True,f);y=run(False,f)
 if x!=y:(HERE/'selector9-probe-failure.json').write_text(json.dumps(dict(fixture=f,stock=x,source=y),indent=2));raise AssertionError((f,x,y))
 rows.append(dict(fixture=f,result=x))
out=dict(status='PASS_SELECTOR9_PROBE',cases=len(rows),base_elf_sha256=c['sha256'],original_bodies={str(k):dict(start=hex(v[0]),end=hex(v[1]),sha256=hashlib.sha256(blob[v[0]-0x410000:v[1]-0x410000]).hexdigest(),visited=len(visited[k]),bytes=v[1]-v[0]) for k,v in extents.items()},results=rows,limits=['Clock/timer/SCS accesses are synthetic registers; no peripheral W1C or concurrency proof.','Integrated image executes native delay/timer service, stop, TON adjust, equality wait and downstream source providers from225-object probe; only unavailable resident ROM delay40 is stubbed with recorded inputs. No source-side locked instruction execution.','Ready-after delay counts are synthetic MMIO stimuli, not observed IRQ scheduling or physical time.','Standalone selector9 probe; not compiler-installed into the transition table, capability bit unchanged.'])
(HERE/'selector9-probe-comparison.json').write_text(json.dumps(out,indent=2));print('PASS',len(rows),{k:len(v) for k,v in visited.items()},'original body bytes')
