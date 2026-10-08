#!/usr/bin/env python3
"""Native runtime action/state/delete/release vs original instructions."""
from pathlib import Path
import importlib.util,json,hashlib,struct,itertools,argparse
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[6];HERE=Path(__file__).parent
s=importlib.util.spec_from_file_location('er',ROOT/'g2/components/bootloader/update_core/elf_reader.py');er=importlib.util.module_from_spec(s);s.loader.exec_module(er)
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);args=ap.parse_args()
base=addon=args.elf;_,bs,sy=er.elf_info(base);ads=[];ns=sy
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
entries={'action':(0x416200,0x41623a),'guard':(0x41602a,0x416058),'state':(0x417fe4,0x41806e),'delete':(0x417f0a,0x417fa8),'release':(0x418ae8,0x418b28),'dfu':(0x42ddda,0x42ddf2),'manager':(0x42e3ca,0x42e3e0)};visited={n:set() for n in entries};rows=[]
def run(source,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,sz in [(0x10000,0x10000),(0x30000,0x10000),(0x410000,0x30000),(0x20000000,0x40000),(0xe000e000,0x1000)]:u.mem_map(lo,sz)
 if source:
  for x in bs+ads:u.mem_write(x['address'],x['data'])
 else:u.mem_write(0x410000,blob)
 def w(p,v):u.mem_write(p,struct.pack('<I',v&0xffffffff))
 kind=f.get('entry','action')
 T=0x20003000;CURRENT=T if f['self'] else 0x20003200
 for p,v in [(0x20027134,CURRENT),(0x20027138,0x20026f34),(0x2002713c,0x20026f48),(0x20027144,8),(0x20027150,f['running']),(0x2002716c,f['suspended']),(0x20027160,10),(0x20027140,2),(0x200004c4,0)]:w(p,v)
 lists=[0x20024870,0x20026f34,0x20026f48,0x20026f84,0x20026f70,0x20002000]
 for l in lists:
  for i,v in enumerate([0,l+8,0xffffffff,l+8,l+8]):w(l+4*i,v)
 w(0x20027164,123456);state={'ready':lists[0],'delayed':lists[1],'overflow':lists[2],'suspended':lists[3],'deleted':lists[4],'none':0}[f['state']]
 def link(l,item):
  w(l,1);w(l+12,item);w(l+16,item)
  for i,v in enumerate([17,l+8,l+8,T,l]):w(item+4*i,v)
 if state:link(state,T+4)
 if f['event']:link(lists[5],T+24)
 w(0x200004d4,0 if f['null'] else T);w(0x200004fc,0 if f['null'] else T);w(T+0x30,0x20006000);u.mem_write(T+0x6c,bytes([f['notify'],f['ownership']]))
 regs=[a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3];vals=[0 if f['null'] else T,0x11223344,0x55667788,0x99aabbcc]
 for r,v in zip(regs,vals):u.reg_write(r,v)
 for r in range(a.UC_ARM_REG_R4,a.UC_ARM_REG_R11+1):u.reg_write(r,0xcafe0000+r)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x3ff01);u.reg_write(a.UC_ARM_REG_PRIMASK,f['mask']);u.reg_write(a.UC_ARM_REG_BASEPRI,f['basepri']);u.reg_write(a.UC_ARM_REG_IPSR,f['ipsr'])
 frees=[];events=[];writes=[];done=False;asserted=False;fault=None
 def code(cpu,pc,size,_):
  nonlocal done,asserted
  if pc==0x3ff00:done=True;cpu.emu_stop();return
  if not source:
   for n,(lo,hi) in entries.items():
    if lo<=pc<hi:visited[n].update(range(pc,pc+size))
  if pc==((sy['opencfw_bl_rtos_free']&~1) if source else 0x419830):
   frees.append(cpu.reg_read(a.UC_ARM_REG_R0));cpu.reg_write(a.UC_ARM_REG_R0,0x12345678);cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if source and 0x410000<=pc<0x440000:raise AssertionError(('unbound source',hex(pc)))
 def write(cpu,access,p,size,v,_):
  if p==0xe000ed04:events.append(['pend',v])
  if 0x200004c4<=p<0x200004c8 or 0x20002000<=p<0x20003300 or 0x20024870<=p<0x20027180:writes.append([p,size,v])
 def invalid(cpu,access,p,size,v,_):
  nonlocal asserted,fault
  asserted=True;fault=[access,p,size];cpu.emu_stop();return False
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
 kind=f.get('entry','action');names={'action':'opencfw_boot_runtime_action','delete':'opencfw_boot_thread_delete','state':'opencfw_boot_thread_state','release':'opencfw_boot_thread_release_storage','dfu':'opencfw_boot_dfu_thread_deinit_native','manager':'opencfw_boot_manager_thread_deinit'}
 entry=ns[names[kind]] if source else entries[kind][0]
 try:u.emu_start(entry|1,0,count=10000)
 except UcError:
  if not asserted:raise
 assert done or asserted,f
 return dict(done=done,asserted=asserted,fault=fault,r0=u.reg_read(a.UC_ARM_REG_R0) if done and kind in ['action','state','manager','dfu'] else None,r1=u.reg_read(a.UC_ARM_REG_R1) if done and kind=='action' else None,sp=u.reg_read(a.UC_ARM_REG_SP) if done else None,callee=[u.reg_read(r) for r in range(a.UC_ARM_REG_R4,a.UC_ARM_REG_R11+1)] if done else None,primask=u.reg_read(a.UC_ARM_REG_PRIMASK),basepri=u.reg_read(a.UC_ARM_REG_BASEPRI),frees=frees,events=events,writes=writes,lists=[bytes(u.mem_read(l,20)).hex() for l in lists],tcb=bytes(u.mem_read(T,112)).hex(),globals=bytes(u.mem_read(0x20027134,80)).hex(),handles=bytes(u.mem_read(0x200004d4,4)).hex()+bytes(u.mem_read(0x200004fc,4)).hex())
fixtures=[]
for state,self_,event,notify,ownership in itertools.product(['ready','delayed','overflow','suspended','deleted','none'],[False,True],[False,True],[0,1],[0,1,2,3]):
 fixtures.append(dict(state=state,self=self_,event=event,notify=notify,ownership=ownership,running=1,suspended=0,mask=0,basepri=0,ipsr=0,null=False))
for null,mask,bp,ipsr,running,suspended in itertools.product([False,True],[0,1],[0,48],[0,16],[0,1],[0,1]):
 fixtures.append(dict(state='ready',self=False,event=False,notify=0,ownership=2,running=running,suspended=suspended,mask=mask,basepri=bp,ipsr=ipsr,null=null))
for kind,null,running,suspended in [('delete',True,1,0),('delete',True,0,0),('delete',True,1,1),('state',True,1,0)]:
 fixtures.append(dict(entry=kind,state='ready',self=True,event=True,notify=0,ownership=2,running=running,suspended=suspended,mask=0,basepri=0,ipsr=0,null=null))
fixtures=[dict(f,entry=k) for f in fixtures if 'entry' not in f for k in ['dfu','manager']]
for f in fixtures:
 x,y=run(False,f),run(True,f)
 if x!=y:
  (HERE/'failure-native-teardown.json').write_text(json.dumps(dict(fixture=f,stock=x,source=y),indent=2)+'\n');raise AssertionError(('differential',f,[k for k in x if x[k]!=y[k]]))
 rows.append(dict(fixture=f,result=x))
out=dict(status='PASS',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),base_elf_sha256=H(base),addon_elf_sha256=H(addon),coverage={n:dict(start=hex(lo),end_exclusive=hex(hi),extent_bytes=hi-lo,body_sha256=hashlib.sha256(blob[lo-0x410000:hi-0x410000]).hexdigest(),visited_bytes=len(visited[n]),unvisited=[hex(x) for x in sorted(set(range(lo,hi))-visited[n])]) for n,(lo,hi) in entries.items()},comparisons=rows,limits=['Actual original/source guard,state,delete,release and existing native list/critical/scheduler helpers execute; allocator419830 is a controlled call boundary recording freed addresses.','Self-delete PendSV request is observed; no context switch, idle cleanup or memory reclamation executes. Invalid configuration cases stop on the original invalid-address write after actual interrupt masking.','Intrusive list/TCB/global state is synthetic; no real task or hardware writes.'])
(HERE/'comparison-native-teardown.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(rows),{n:len(v) for n,v in visited.items()})
