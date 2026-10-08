from pathlib import Path
import json,struct,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import *
import unicorn.arm_const as a
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());c=json.loads((N/'current-candidate.json').read_text());elf=R/c['directory']/'candidate.elf';blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(int(s['p_vaddr']),s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:int(s['st_value']) for s in e.get_section_by_name('.symtab').iter_symbols()}
spans={'profile':(0x42ab7c,0x42abb2),'temperature':(0x42ac54,0x42aca4)};names={'profile':'opencfw_pcm22_profile_apply','temperature':'opencfw_pcm22_temperature_init'};visited={k:set() for k in spans}
def run(stock,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for p,s in [(0,4096),(0x10000,65536),(0x30000,65536),(0x50000,65536),(0x410000,0x30000),(0x20000000,0x40000),(0x40000000,0x300000),(0x8000000,4096)]:u.mem_map(p,s)
 if stock:u.mem_write(0x410000,blob)
 else:
  for p,b in segments:u.mem_write(p,b)
 def w(p,v):u.mem_write(p,struct.pack('<I',v&0xffffffff))
 w(0x20026ba0,f.get('magic',0));w(0x20026bc0,f.get('core',0));w(0x20026c08,f.get('vref',0));w(0x40020080,0xa5a55a5a);w(0x40020088,0x55aa55aa);w(0x400201b0,0xf00dcafe);w(0x40021008,f.get('first',0));w(0x40021010,f.get('second',0));w(0x400083e0,0x110)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_PRIMASK,f['mask']);u.reg_write(a.UC_ARM_REG_FPSCR,f.get('fpscr',0));u.mem_write(0x8000000,b'\x00\xbf\xfe\xe7')
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xaac000+i)
 calls=[];writes=[];done=[False]
 entries={(0x41bf84 if stock else sy['opencfw_bl_mspi_mode_enter']&~1):'power',(0x41ca2c if stock else sy['opencfw_boot_startup_temperature']&~1):'setter',(0x41d21c if stock else sy['opencfw_boot_control_delay_status_change']&~1):'poll'}
 def code(cpu,pc,size,_):
  if pc in [0x8000000,0x8000002]:done[0]=True;cpu.emu_stop();return
  if stock:
   start,end=spans[f['kind']]
   if start<=pc<end:visited[f['kind']].update(range(pc,pc+size))
  if pc in entries:
   name=entries[pc];args=[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)]
   if name=='power':assert args[0]==29;calls.append(dict(name=name,selector=args[0]))
   elif name=='setter':
    assert 0x2003e000<=args[0]<0x2003f000;assert cpu.reg_read(a.UC_ARM_REG_S0)==0xc2200000;w(args[0],0x12345678);w(args[0]+4,0xabcdef01);calls.append(dict(name=name,s0=cpu.reg_read(a.UC_ARM_REG_S0),output='stack8'))
   else:assert args==[2500,0x400083e0,1,0];calls.append(dict(name=name,args=args))
   cpu.reg_write(a.UC_ARM_REG_R0,f.get(name,0));cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if not stock and 0x410000<=pc<0x435000:raise AssertionError(('source official code',hex(pc)))
 def store(cpu,access,p,size,v,_):
  if 0x40000000<=p<0x40300000:writes.append([p,size,v&((1<<(8*size))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,store);u.emu_start((spans[f['kind']][0] if stock else sy[names[f['kind']]])|1,0,count=50000);assert done[0]
 return dict(ret=u.reg_read(a.UC_ARM_REG_R0),sp=u.reg_read(a.UC_ARM_REG_SP),mask=u.reg_read(a.UC_ARM_REG_PRIMASK),fpscr=u.reg_read(a.UC_ARM_REG_FPSCR),saved=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],calls=calls,writes=writes)
fixtures=[]
for magic,core,vref,mask in itertools.product([0,0x1f01600d,0xffffffff],[0,0x12345678,0xffffffff],[0,1,2,3,0xabcdef01,0xffffffff],[0,1]):fixtures.append(dict(kind='profile',magic=magic,core=core,vref=vref,mask=mask))
for first,second,power,setter,poll,mask in itertools.product([0,1],[0,2],[0,1,7],[0,1,7],[0,1,4],[0,1]):fixtures.append(dict(kind='temperature',first=first,second=second,power=power,setter=setter,poll=poll,mask=mask))
rows=[]
for f in fixtures:
 x=run(True,f);y=run(False,f)
 if x!=y:(N/'hooks-failure.json').write_text(json.dumps(dict(fixture=f,stock=x,source=y),indent=2));raise AssertionError((f,x,y))
 rows.append(dict(fixture=f,result=x))
out=dict(status='PASS_PCM22_RUNTIME_HOOKS_WITH_CHILD_CONTRACTS',cases=len(rows),candidate_sha256=c['sha256'],original_bodies={k:dict(start=hex(s),end=hex(z),bytes=z-s,visited=len(visited[k]),sha256=hashlib.sha256(blob[s-0x410000:z-0x410000]).hexdigest()) for k,(s,z) in spans.items()},results=rows,limits=['Temperature power-enter29, hard-float setter and status-poll children are explicit return fixtures; their internal behavior is not proved here.','Original bodies execute on stock side and compiled bodies on source; no original source-side execution.','Local setter output pointer normalized after mapped stack8-byte bound; physical clocks/power/IRQ behavior unproved.'])
(N/'hooks-comparison.json').write_text(json.dumps(out,indent=2));print(out['status'],len(rows),{k:len(v) for k,v in visited.items()})
