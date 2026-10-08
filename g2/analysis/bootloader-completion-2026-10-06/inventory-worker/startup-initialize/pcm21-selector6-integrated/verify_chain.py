"""Original-instruction oracles, with explicit sampler/critical/scheduler/deep-sleep cuts."""
from pathlib import Path
import json,hashlib,itertools,struct
from unicorn import *
from unicorn import arm_const as a
from elftools.elf.elffile import ELFFile
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5';elf=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/build/bootloader-completion/pcm21-selector6-integrated/c528f8bed79c3d55ce1d2b47db974b28ed0f63240bd0cc8c8f6d17d1f09fb76e/candidate.elf')
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
roles={'enter':(0x41b3e4,0x0800e000,0),'exit':(0x41b3fc,0x0800e010,0),'mask':(0x41b2f8,0x0800e020,0),'sample':(0x422aac,0x0800e030,2),'save':(0x41b8ec,0x0800e040,0),'deep':(0x41a71e,0x0800e050,1),'cleanup':(0x418a98,0x0800e060,0),'resched':(0x41b3d0,0x0800e070,0),'suspend':(0x4181d8,0x0800e080,0),'resume':(0x418228,0x0800e090,0),'sleep':(0x41b754,0x0800e0a0,1),'expected':(0x4181e4,0x0800e0b0,0)}
for role,symbol in [('cleanup','cleanup'),('resched','reschedule'),('suspend','suspend_scheduler'),('resume','resume_scheduler'),('deep','deep_sleep')]:
 orig,stub,argc=roles[role];roles[role]=(orig,sy[symbol]&~1,argc)
roles.update({'cpget':(0x41ca0c,0x0800d000,1),'cpset':(0x41c9ca,0x0800d010,1),'power':(0x41cd1a,0x0800d020,3),'buck':(0x41c838,0x0800d030,1),'lpen':(0x41ce26,0x0800d040,0),'lpdis':(0x41ce3c,0x0800d050,0),'delay':(0x41d1c0,0x0800d060,1),'boost':(0x41cdb8,0x0800d070,0)})
for role,symbol in [('cpget','cp_get'),('cpset','cp_set'),('buck','buck_override'),('lpen','lp_enable'),('lpdis','lp_disable'),('power','power_state'),('delay','delay_one'),('boost','boost_service')]:
 orig,stub,argc=roles[role];roles[role]=(orig,sy[symbol]&~1,argc)
ranges={'step_ticks':(0x418394,0x418408),'counter_read':(0x41f424,0x41f440),'timer_compare':(0x41f440,0x41f4ac),'stimer_interrupt_clear':(0x41f4b6,0x41f4c0),'irq_clear':(0x41b630,0x41b64c),'pre_sleep':(0x41b5e8,0x41b5f4),'post_sleep':(0x41b5f4,0x41b5f6),'sample_three':(0x422aac,0x422ac8),'irq_save':(0x41b8ec,0x41b8f4),'idle_entry':(0x4189ac,0x4189fa),'tickless_sleep':(0x41b754,0x41b818),'deep_sleep':(0x41a71e,0x41ac44),'cp_get':(0x41ca0c,0x41ca2c),'cp_set':(0x41c9ca,0x41ca08),'lp_enable':(0x41ce26,0x41ce3c),'lp_disable':(0x41ce3c,0x41ce52)};covered=set();rows=[]
def run(name,src,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for adr,n in [(0x410000,0x30000),(0x08000000,0x10000),(0x10000,0x10000),(0x30000,0x10000),(0x50000,0x10000),(0x20000000,0x40000),(0x40008000,0x2000),(0x40020000,0x2000),(0x47ff0000,0x1000),(0xe000e000,0x2000),(0xe001e000,0x1000)]:u.mem_map(adr,n)
 u.mem_write(0x410000,raw)
 for adr,b in segments:u.mem_write(adr,b)
 def w(adr,v):u.mem_write(adr,struct.pack('<I',v&0xffffffff))
 def rd(adr):return struct.unpack('<I',u.mem_read(adr,4))[0]
 for adr,v in {0x20027148:f.get('ticks',10),0x20027164:f.get('next',100),0x2002716c:f.get('suspended',1),0x20027154:0 if name=='idle_entry' else 7,0x200004c4:0,0x200001c8:f.get('last',100),0x20024870:f.get('ready',1),0x20027134:0x20030000,0x2003002c:0,0x2002714c:0,0x20027120:100,0x20027124:10,0x20027128:9,0x40008904:0xabcdef}.items():w(adr,v)
 for adr,val in {0x40021000:f.get('perf',0),0x40021108:f.get('simo',0),0x40021008:f.get('otp',0),0x4002000c:f.get('rev',0x22),0x20000098:f.get('pcm',2),0x40020344:f.get('trim',0x0a000000),0x20026ba0:f.get('info',0x1f01600d),0x20026bf4:0x40,0x20026c08:0x00700000,0x4002037c:0x48,0xe000ed10:0}.items():w(adr,val)
 for adr,key in [(0x200271b0,'hp_to_deep'),(0x200271af,'override'),(0x200271ad,'pcm22'),(0x200271a9,'pcm21'),(0x200271b2,'switching'),(0x200271b1,'lpminus'),(0x200271c1,'appforce'),(0x200271c0,'force')]:u.mem_write(adr,bytes([f.get(key,0)]))
 act=f.get('act',[1,1,1]);w(0xe001e300,(act[0]<<8)|(act[1]<<4)|act[2]);w(0xe000ed14,f.get('ccr',0));w(0x40021010,f.get('aud',0));w(0x400204d8,f.get('pll',0));w(0x20026e6c,0x0800c001 if f.get('callback') else 0);w(0x20026e70,0x0800c001 if f.get('callback') else 0)
 # Coherent static kernel list heads; no allocator fixture is cut.
 if name=='idle_entry':
  for adr in [0x20026f34,0x20026f48,0x20026f5c,0x20026f70,0x20026f84]:
   for off,v in [(0,0),(4,adr+8),(8,0xffffffff),(12,adr+8),(16,adr+8)]:w(adr+off,v)
  w(0x20027138,0x20026f34);w(0x2002713c,0x20026f48);w(0x20027144,1);w(0x2002716c,0)
  if f.get('deleted'):
   item=0x20031004;head=0x20026f78
   for adr,v in [(0x20026f70,1),(0x20026f7c,item),(0x20026f80,item),(item+4,head),(item+8,head),(item+12,0x20031000),(item+16,0x20026f70),(0x20027140,1),(0x20027144,2)]:w(adr,v)
   u.mem_write(0x2003106d,bytes([2]))
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x0800ff01);u.reg_write(a.UC_ARM_REG_R0,f.get('r0',0));u.reg_write(a.UC_ARM_REG_R1,f.get('r1',0));u.reg_write(a.UC_ARM_REG_PRIMASK,f.get('mask',0))
 calls=[];writes=[];samples=0;expects=0;cleanups=0;end=[];mmio_reads=[];wakes=0
 def hook(cpu,pc,n,_):
  nonlocal samples,expects,cleanups,wakes
  if pc==0x0800ff00:end.append('return');u.emu_stop();return
  if pc==0x0800c000:calls.append(['low-power-callback']);u.reg_write(a.UC_ARM_REG_R0,7);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if not src:
   for lo,hi in ranges.values():
    if lo<=pc<hi:covered.update(range(pc,pc+n))
  if bytes(u.mem_read(pc,n))==bytes.fromhex('30bf'):
   wakes+=1;calls.append(['synthetic-wake',wakes]);w(0xe000ed04,0x62000 if f.get('boost_wake') and wakes==1 else 0);u.reg_write(a.UC_ARM_REG_PC,(pc+n)|1);return
  for role,(orig,stub,argc) in roles.items():
   if pc!=(stub if src else orig):continue
   if role in ['sample','save','enter','exit','mask','expected','sleep','deep','cpget','cpset','buck','lpen','lpdis']:continue
   if role=='expected' and name!='idle_entry':continue
   if role in ['cleanup','resched','suspend','resume']:
    calls.append([role,[]])
    if role=='cleanup':
     cleanups+=1
     if cleanups==2:end.append('second-idle-iteration');u.emu_stop();return
    if role=='suspend':
     if 'post_next' in f:w(0x20027164,f['post_next'])
     if 'post_pending' in f:w(0x20027154,f['post_pending'])
    continue
   regs=[u.reg_read(getattr(a,'UC_ARM_REG_R'+str(i))) for i in range(argc)]
   if role in ['cpget','cpset','power','buck','lpen','lpdis','delay','boost']:
    if role=='cpget':
     vals=f.get('act',[1,1,1]);u.mem_write(regs[0],bytes(vals));calls.append([role,vals])
    elif role=='power':calls.append([role,regs[:2]+[bytes(u.mem_read(regs[2],1))[0]]])
    else:calls.append([role,regs])
    if role=='delay':
     if f.get('other_after_delay') and wakes:w(0xe000ed04,0x3000)
     else:w(0x40021000,(rd(0x40021000)&~24)|16)
    if role=='boost':
     w(0xe000ed04,f.get('other_irq',0)<<12)
     if f.get('boost_wait'):w(0x40021000,2)
    u.reg_write(a.UC_ARM_REG_R0,0);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
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
  raise RuntimeError(name,f,hex(adr),hex(u.reg_read(a.UC_ARM_REG_PC)))
 def read(cpu,access,adr,size,value,_):
  nonlocal samples
  if adr==0x40008804:
   values=f.get('samples');v=values[min(samples//3,len(values)-1)][samples%3] if values else 100+samples//3;samples+=1;w(adr,v);mmio_reads.append([adr,v,u.reg_read(a.UC_ARM_REG_PRIMASK)])
 def write(cpu,access,adr,size,value,_):writes.append([adr,size,value])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,mem);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_READ,read)
 try:u.emu_start((sy[name] if src else ranges[name][0])|1,0,count=20000)
 except UcError:
  if not end:raise RuntimeError(name,src,f,hex(u.reg_read(a.UC_ARM_REG_PC)))
 assert end,(name,f)
 observed={hex(adr):rd(adr) for adr in [0x20027148,0x20027154,0x200004c4,0x200001c8,0x40008820,0x40008908,0x20027140,0x20027144,0x20026f70,0x2002716c,0xe000ed10,0xe001e300,0x40020344,0x40020374,0x4002037c,0x40020060]}
 result=dict(end=end,calls=calls,mmio_reads=mmio_reads,state=observed,primask=u.reg_read(a.UC_ARM_REG_PRIMASK),basepri=u.reg_read(a.UC_ARM_REG_BASEPRI),mmio_writes=[x for x in writes if 0x40000000<=x[0]<0x50000000 or 0xe000e000<=x[0]<0xe0010000])
 if name in ['counter_read','timer_compare','stimer_interrupt_clear','pre_sleep','deep_sleep','cp_set','lp_enable','lp_disable']:result['return']=u.reg_read(a.UC_ARM_REG_R0)
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
for ready,post_next,pending in itertools.product([1,2],[10,100],[0,1]):fixtures.append(('idle_entry',dict(ready=ready,expected=[100],next=100,ticks=10,post_next=post_next,post_pending=pending,deleted=True)))
for deep,otp,simo,perf,mask,flags,boost in itertools.product([0,1,2],[0,0x08000000],[0,0x30],[0,2,18],[0,1],[0,1],[0,1]):
 fixtures.append(('deep_sleep',dict(r0=deep,otp=otp,simo=simo,perf=perf,mask=mask,hp_to_deep=flags,override=flags,pcm21=flags,lpminus=flags,boost_wake=boost)))
for act in [[0,2,1],[2,3,2]]:fixtures.append(('deep_sleep',dict(r0=1,act=act,pcm22=1,boost_wake=1,other_irq=3,rev=0x23,pcm=1,simo=0x30)))
for config,ccr in itertools.product([0,0x010101,0x030203,0x020103],[0,0x10000,0x20000]):fixtures.append(('cp_set',dict(r0=config,ccr=ccr)))
for extra in [dict(appforce=1),dict(force=1),dict(rev=0x24,aud=4),dict(rev=0x24,pll=0x20000000),dict(switching=1),dict(info=0),dict(trim=0x02000000),dict(boost_wait=1,other_after_delay=1),dict(callback=1)]:
 f=dict(r0=1,simo=0x30,perf=18,hp_to_deep=1,override=1,pcm21=1,lpminus=1,boost_wake=1);f.update(extra);fixtures.append(('deep_sleep',f))
for name in ['lp_enable','lp_disable']:
 for callback in [0,1]:fixtures.append((name,dict(callback=callback)))
for name,f in fixtures:
 x=run(name,False,f);y=run(name,True,f);assert x==y,(name,f,x,y);rows.append(dict(function=name,fixture=f,result=x))
out=dict(status='PASS',cases=len(rows),blob_sha256=hashlib.sha256(raw).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),coverage={name:dict(start=hex(lo),end=hex(hi),bytes=hi-lo,covered=sum(x in covered for x in range(lo,hi))) for name,(lo,hi) in ranges.items()},results=rows,limits=['Native sampler/IRQ-save/critical helpers/sleep policy/tickless/tick-step/timer wrappers execute. Idle cleanup/reschedule/suspend/resume are now native; Deep-sleep body now executes; cp-state/spot-manager/buck/boost/delay subcalls and WFI wake remain modeled boundaries.','MMIO is synthetic memory; no Apollo counter timing, W1C effects, NVIC pending delivery or deep sleep. Full idle is compared to the next iteration, not run as a live scheduler.'])
(HERE/'comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['cases'],out['coverage'])
