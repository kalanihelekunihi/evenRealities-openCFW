"""Original-instruction oracles, with explicit sampler/critical/scheduler/deep-sleep cuts."""
from pathlib import Path
import json,hashlib,itertools,struct
from unicorn import *
from unicorn import arm_const as a
from elftools.elf.elffile import ELFFile
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5';elf=Path('/tmp/opencfw-idle-chain.elf')
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
roles={'enter':(0x41b3e4,0x0800e000,0),'exit':(0x41b3fc,0x0800e010,0),'mask':(0x41b2f8,0x0800e020,0),'sample':(0x422aac,0x0800e030,2),'save':(0x41b8ec,0x0800e040,0),'deep':(0x41a71e,0x0800e050,1),'cleanup':(0x418a98,0x0800e060,0),'resched':(0x41b3d0,0x0800e070,0),'suspend':(0x4181d8,0x0800e080,0),'resume':(0x418228,0x0800e090,0),'sleep':(0x41b754,0x0800e0a0,1),'expected':(0x4181e4,0x0800e0b0,0)}
ranges={'step_ticks':(0x418394,0x418408),'counter_read':(0x41f424,0x41f440),'timer_compare':(0x41f440,0x41f4ac),'stimer_interrupt_clear':(0x41f4b6,0x41f4c0),'irq_clear':(0x41b630,0x41b64c),'pre_sleep':(0x41b5e8,0x41b5f4),'post_sleep':(0x41b5f4,0x41b5f6),'sample_three':(0x422aac,0x422ac8),'irq_save':(0x41b8ec,0x41b8f4),'idle_entry':(0x4189ac,0x4189fa),'tickless_sleep':(0x41b754,0x41b818)};covered=set();rows=[]
def run(name,src,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for adr,n in [(0x410000,0x30000),(0x08000000,0x10000),(0x20000000,0x40000),(0x40008000,0x2000),(0xe000e000,0x2000)]:u.mem_map(adr,n)
 u.mem_write(0x410000,raw)
 for adr,b in segments:u.mem_write(adr,b)
 def w(adr,v):u.mem_write(adr,struct.pack('<I',v&0xffffffff))
 def rd(adr):return struct.unpack('<I',u.mem_read(adr,4))[0]
 for adr,v in {0x20027148:f.get('ticks',10),0x20027164:f.get('next',100),0x2002716c:f.get('suspended',1),0x20027154:0 if name=='idle_entry' else 7,0x200004c4:0,0x200001c8:f.get('last',100),0x20024870:f.get('ready',1),0x20027134:0x20030000,0x2003002c:0,0x2002714c:0,0x20027120:100,0x20027124:10,0x20027128:9,0x40008904:0xabcdef}.items():w(adr,v)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x0800ff01);u.reg_write(a.UC_ARM_REG_R0,f.get('r0',0));u.reg_write(a.UC_ARM_REG_R1,f.get('r1',0));u.reg_write(a.UC_ARM_REG_PRIMASK,f.get('mask',0))
 calls=[];writes=[];samples=0;expects=0;cleanups=0;end=[];mmio_reads=[]
 def hook(cpu,pc,n,_):
  nonlocal samples,expects,cleanups
  if pc==0x0800ff00:end.append('return');u.emu_stop();return
  if not src:
   for lo,hi in ranges.values():
    if lo<=pc<hi:covered.update(range(pc,pc+n))
  for role,(orig,stub,argc) in roles.items():
   if pc!=(stub if src else orig):continue
   if role in ['sample','save','enter','exit','mask','expected','sleep']:continue
   if role=='expected' and name!='idle_entry':continue
   regs=[u.reg_read(getattr(a,'UC_ARM_REG_R'+str(i))) for i in range(argc)]
   if role=='sample':
    assert regs[0]==0x40008804,hex(regs[0]);values=f.get('samples',[[100,100,100],[101,101,101],[102,102,102],[103,103,103],[104,104,104]]);v=values[min(samples,len(values)-1)];samples+=1
    for i,x in enumerate(v):w(regs[1]+4*i,x)
    calls.append([role,regs[0],v]);u.reg_write(a.UC_ARM_REG_R0,regs[1])
   else:
    calls.append([role,regs])
    if role=='enter':w(0x200004c4,rd(0x200004c4)+1);u.reg_write(a.UC_ARM_REG_BASEPRI,48)
    if role=='exit':w(0x200004c4,rd(0x200004c4)-1);u.reg_write(a.UC_ARM_REG_BASEPRI,0)
    if role=='mask':u.reg_write(a.UC_ARM_REG_BASEPRI,48)
    if role=='save':old=u.reg_read(a.UC_ARM_REG_PRIMASK);u.reg_write(a.UC_ARM_REG_PRIMASK,1);u.reg_write(a.UC_ARM_REG_R0,old)
    if role=='expected':v=f['expected'][min(expects,len(f['expected'])-1)];expects+=1;u.reg_write(a.UC_ARM_REG_R0,v)
    if role=='suspend':
     w(0x2002716c,rd(0x2002716c)+1)
     if 'post_next' in f:w(0x20027164,f['post_next'])
     if 'post_pending' in f:w(0x20027154,f['post_pending'])
    if role=='resume':w(0x2002716c,rd(0x2002716c)-1)
    if role=='cleanup':
     cleanups+=1
     if cleanups==2:end.append('second-idle-iteration');u.emu_stop();return
   u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
 def mem(cpu,access,adr,size,value,_):
  if adr==0xffffffff:end.append('assertion-write');u.emu_stop();return False
  return False
 def read(cpu,access,adr,size,value,_):
  nonlocal samples
  if adr==0x40008804:
   values=f.get('samples');v=values[min(samples//3,len(values)-1)][samples%3] if values else 100+samples//3;samples+=1;w(adr,v);mmio_reads.append([adr,v,u.reg_read(a.UC_ARM_REG_PRIMASK)])
 def write(cpu,access,adr,size,value,_):writes.append([adr,size,value])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,mem);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_READ,read)
 try:u.emu_start((sy[name] if src else ranges[name][0])|1,0,count=1000)
 except UcError:
  if not end:raise
 assert end,(name,f)
 observed={hex(adr):rd(adr) for adr in [0x20027148,0x20027154,0x200004c4,0x200001c8,0x40008820,0x40008908]}
 result=dict(end=end,calls=calls,mmio_reads=mmio_reads,state=observed,primask=u.reg_read(a.UC_ARM_REG_PRIMASK),basepri=u.reg_read(a.UC_ARM_REG_BASEPRI),mmio_writes=[x for x in writes if 0x40000000<=x[0]<0x50000000 or 0xe000e000<=x[0]<0xe0010000])
 if name in ['counter_read','timer_compare','stimer_interrupt_clear','pre_sleep']:result['return']=u.reg_read(a.UC_ARM_REG_R0)
 return result
fixtures=[]
for ticks,nxt,jump,suspended in itertools.product([0,10,0xfffffff0],[0,10,15,100,0xffffffff],[0,1,5,100],[0,1]):fixtures.append(('step_ticks',dict(ticks=ticks,next=nxt,r0=jump,suspended=suspended)))
for values in [[1,1,2],[1,2,3],[0xffffffff,0,1]]:fixtures.append(('counter_read',dict(samples=[values])))
for channel,delta,mask in itertools.product([0,1,7,8],[0,1,3,4,10,100],[0,1]):fixtures.append(('timer_compare',dict(r0=channel,r1=delta,mask=mask)))
for bits in [0,1,0xffffffff]:fixtures.append(('stimer_interrupt_clear',dict(r0=bits)))
for irq in [0,31,32,63,0xffff,0xffff8000]:fixtures.append(('irq_clear',dict(r0=irq)))
for expected in [0,1,100]:fixtures.extend([('pre_sleep',dict(r0=expected)),('post_sleep',dict(r0=expected))])
for ready,expect,nxt,ticks in itertools.product([1,2],[[0],[3,0],[3,4]],[5,100],[10]):fixtures.append(('idle_entry',dict(ready=ready,expected=expect,next=nxt,ticks=ticks)))
for post_next,post_pending in itertools.product([10,11,100],[0,1]):fixtures.append(('idle_entry',dict(ready=1,expected=[100],next=100,ticks=10,post_next=post_next,post_pending=post_pending)))
fixtures.append(('timer_compare',dict(r0=0,r1=10,last=0xfffffffc,samples=[[0xfffffffe]*3,[0xffffffff]*3,[0]*3,[1]*3])))
for name,f in fixtures:
 x=run(name,False,f);y=run(name,True,f);assert x==y,(name,f,x,y);rows.append(dict(function=name,fixture=f,result=x))
out=dict(status='PASS',cases=len(rows),blob_sha256=hashlib.sha256(raw).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),coverage={name:dict(start=hex(lo),end=hex(hi),bytes=hi-lo,covered=sum(x in covered for x in range(lo,hi))) for name,(lo,hi) in ranges.items()},results=rows,limits=['Native sampler/IRQ-save/critical helpers/sleep policy/tickless/tick-step/timer wrappers execute. Deep-sleep and idle cleanup/reschedule/suspend/resume calls remain modeled boundaries.','MMIO is synthetic memory; no Apollo counter timing, W1C effects, NVIC pending delivery or deep sleep. Full idle is compared to the next iteration, not run as a live scheduler.'])
(HERE/'comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['cases'],out['coverage'])
