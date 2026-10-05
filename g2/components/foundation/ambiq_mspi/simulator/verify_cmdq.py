#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Bounded ARM32 CMDQ/lifecycle comparison; critical entry and delay synthetic."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
if not __debug__: raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/foundation/touch_scb/simulator/verify.py'); elfmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(elfmod)
H,Q,T,G,R,STOP=0x20001000,0x20003000,0x20004000,0x200523d8,0x40060000,0x8000000
BASE=0x438000
FUN={'cq_disable':(0x538e8c,66,'am_hal_cmdq_disable'),'cq_term':(0x53909a,98,'am_hal_cmdq_term'),'wrapper_disable':(0x4bfd62,12,'mspi_cq_disable'),'wrapper_term':(0x4bfc86,58,'mspi_cq_term'),'disable':(0x4c0ea8,118,'ambiq_sim_controller_disable'),'deinitialize':(0x4c0f24,56,'ambiq_sim_deinitialize')}
def sha(b):return hashlib.sha256(b).hexdigest()
def words(values):return struct.pack('<'+'I'*len(values),*values)
def run(segments,entry,c,syms=None,real_critical=False):
 import unicorn as u
 from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);pages=set()
 for s in segments:
  for a in range(s['address']&~4095,(s['address']+s['memory_size']+4095)&~4095,4096):
   if a not in pages:cpu.mem_map(a,4096);pages.add(a)
  cpu.mem_write(s['address'],s['data'])
 for lo,size in [(0x20000000,0x10000),(0x20050000,0x10000),(R,0x3000),(STOP,4096)]:
  for a in range(lo,lo+size,4096):
   if a not in pages:cpu.mem_map(a,4096);pages.add(a)
 state=bytearray(b'\xa5'*0x8d0)
 for off,val in [(0,c['hpfx']),(4,c['module']),(0x18,c['tcb']),(0x20,c['pending']),(0x828,0 if c['qnull'] else Q),(0x840,c['hp']),(0x8cc,17)]:struct.pack_into('<I',state,off,val)
 cpu.mem_write(H-8,b'\xcc'*8+bytes(state)+b'\xcc'*8)
 q=words([c['qpfx'],0x20008000,0x20008100,0xdeadbeef,0x20008040,0,64,c['cur'],c['end'],T,0]);cpu.mem_write(Q-8,b'\xcc'*8+q+b'\xcc'*8)
 regs=R+c['module']*4096
 cpu.mem_write(T,words([regs+0x280,regs+0x284,regs+0x288,regs+0x28c,regs+0x290,c['mask']]))
 cpu.mem_write(regs+0x280,words([c['cfg'],c['addr'],c['hw'],0,c['pause']]))
 cpu.mem_write(regs+0x90,words([c['xip']]))
 slot=G+c['module']*0x8d0+0x828;cpu.mem_write(slot,words([0 if c['global_null'] else Q]))
 calls=[];mmio=[];trace={};protected_masks=[]
 critical=syms['opencfw_cmdq_critical_enter']&~1 if syms else 0x473940
 delay=syms['am_hal_delay_us']&~1 if syms else 0x4807a0
 if not syms:
  for a in ([delay] if real_critical else [critical,delay]):cpu.mem_write(a,b'\x70\x47')
 def code(uc,a,size,_):
  if a in [critical,delay]:
   calls.append(['critical',c['prior']] if a==critical else ['delay',uc.reg_read(UC_ARM_REG_R0)])
   if a==delay or not real_critical:
    uc.reg_write(UC_ARM_REG_R0,c['prior'] if a==critical else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  raw=bytes(uc.mem_read(a,size));match=[s for s in segments if s['flags']&1 and s['address']<=a and a+size<=s['address']+len(s['data'])];assert len(match)==1
  s=match[0];assert raw==s['data'][a-s['address']:a-s['address']+size];trace[a]=raw.hex()
 def mem(uc,access,a,size,value,_):
  if real_critical and a in [regs+0x284,regs+0x288] and access==u.UC_MEM_READ:
   protected_masks.append(uc.reg_read(UC_ARM_REG_PRIMASK));assert protected_masks[-1]==1
  if R<=a<R+0x3000:
   assert size==4
   mmio.append(['r' if access==u.UC_MEM_READ else 'w',a,struct.unpack('<I',uc.mem_read(a,4))[0] if access==u.UC_MEM_READ else value])
 cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem)
 arg=Q if c['op'].startswith('cq_') else H
 if c['null']:arg=0
 if real_critical:cpu.reg_write(UC_ARM_REG_PRIMASK,c['prior'])
 cpu.reg_write(UC_ARM_REG_R0,arg);cpu.reg_write(UC_ARM_REG_R1,c['force']);cpu.reg_write(UC_ARM_REG_SP,0x2000f000);cpu.reg_write(UC_ARM_REG_LR,STOP|1)
 cpu.emu_start(entry|1,STOP,count=10000);assert cpu.reg_read(UC_ARM_REG_PC)==STOP
 assert bytes(cpu.mem_read(H-8,8))==bytes(cpu.mem_read(H+0x8d0,8))==b'\xcc'*8
 assert bytes(cpu.mem_read(Q-8,8))==bytes(cpu.mem_read(Q+44,8))==b'\xcc'*8
 return dict(status=cpu.reg_read(UC_ARM_REG_R0),state=bytes(cpu.mem_read(H,0x8d0)).hex(),queue=bytes(cpu.mem_read(Q,44)).hex(),slot=bytes(cpu.mem_read(slot,4)).hex(),registers=bytes(cpu.mem_read(regs+0x280,20)).hex(),primask=cpu.reg_read(UC_ARM_REG_PRIMASK),protected_masks=protected_masks,calls=calls,mmio=mmio,trace=trace)
def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--real-critical',action='store_true');a=p.parse_args()
 if a.real_critical:FUN['critical_enter']=(0x473940,8,'am_hal_interrupt_master_disable')
 blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
 # Map only authenticated pages needed by these bounded bodies and literals.
 pages={pc&~4095 for pc,_,_ in FUN.values()} | {0x538d18&~4095,0x53924c&~4095,0x4c08a4&~4095,0x473940&~4095,0x4807a0&~4095}
 original=[dict(address=pc,data=blob[pc-BASE+32:pc-BASE+32+4096],memory_size=4096,flags=5) for pc in sorted(pages)]
 elf,segs,syms=elfmod.elf_info(a.elf)
 default=dict(hpfx=0x3bebebe,qpfx=0x3cdcdcd,module=0,tcb=0x20008000,pending=0,hp=0,qnull=False,global_null=False,cur=0,end=0x102,hw=2,cfg=0x80000001,pause=0xf1234567,mask=0x100,addr=0x20008038,xip=1,prior=0,force=1,null=False)
 variants=[('normal',{}),('already_disabled',{'qpfx':0x1cdcdcd}),('invalid_magic',{'qpfx':0x3cdcdce}),('not_init',{'qpfx':0x2cdcdcd}),('null',{'null':True}),('null_queue',{'qnull':True}),('null_global',{'global_null':True}),('wrap',{'hw':0xff,'end':0x102}),('busy_nonforce',{'force':0,'hw':1}),('idle_nonforce',{'force':0}),('masked_high_index',{'hw':0xffffff02}),('prior_masked',{'prior':1}),('no_mask',{'mask':0}),('all_mask',{'mask':0xffffffff}),('cfg_disabled',{'cfg':0x80000000}),('no_tcb',{'tcb':0}),('pending',{'pending':1}),('hp_pending',{'hp':1}),('disabled_mspi',{'hpfx':0x1bebebe}),('invalid_mspi',{'hpfx':0x3bebebf}),('no_xip',{'xip':0})]
 results=[];observed={}
 for op,(pc,size,symbol) in FUN.items():
  for module in range(3):
   for name,change in variants:
    c=dict(default,op=op,module=module);c.update(change)
    if op in ['wrapper_disable','wrapper_term'] and c['null']:continue # wrappers require a valid mapped MSPI state
    x=run(original,pc,c,real_critical=a.real_critical);y=run(segs,syms[symbol],c,syms,real_critical=a.real_critical)
    xt=x.pop('trace');y.pop('trace');assert x==y,(op,name,module,x,y)
    for k,v in xt.items():observed[k]=v
    # Independent expected leaf assertions, beyond pairwise agreement.
    if op=='critical_enter':
     assert x['status']==c['prior'] and x['primask']==1
    if op=='cq_disable':
     valid=not c['null'] and c['qpfx']&0x1ffffff==0x1cdcdcd
     assert x['status']==(0 if valid else 2)
     expected=c['qpfx']&~0x2000000 if valid else c['qpfx']
     assert struct.unpack_from('<I',bytes.fromhex(x['queue']))[0]==expected
     assert x['calls']==[]
    if op=='cq_term':
     valid=not c['null'] and c['qpfx']&0x1ffffff==0x1cdcdcd
     idx=(c['end']&~255)|(c['hw']&255)
     if (c['end']-idx)&0x80000000:idx=(idx-256)&0xffffffff
     status=2 if not valid else 3 if not c['force'] and idx!=c['end'] else 0
     assert x['status']==status
     if valid:
      assert struct.unpack_from('<I',bytes.fromhex(x['queue']),0x1c)[0]==idx
      assert x['calls']==[['critical',c['prior']]]
      assert x['primask']==c['prior']
    if op=='wrapper_term':assert x['status']==0 and x['slot']=='00000000'
    results.append(dict(operation=op,name=name,inputs=c,result=x,original_trace=xt))
 ranges={}
 for name,(pc,size,_) in FUN.items():ranges[name]=dict(address=hex(pc),declared_size=size,executed_bytes=sum(len(bytes.fromhex(v)) for k,v in observed.items() if pc<=k<pc+size),sha256=sha(blob[pc-BASE+32:pc-BASE+32+size]))
 ranges['update_indices']=dict(address='0x538d18',declared_size=64,executed_bytes=sum(len(bytes.fromhex(v)) for k,v in observed.items() if 0x538d18<=k<0x538d58))
 if a.real_critical:
  pc=syms['am_hal_interrupt_master_disable']&~1
  code=[z for z in segs if z['flags']&1 and z['address']<=pc<pc+8<=z['address']+len(z['data'])];assert len(code)==1
  z=code[0];assert z['data'][pc-z['address']:pc-z['address']+8]==blob[0x473940-BASE+32:0x473948-BASE+32]
  assert all(z['executed_bytes']==z['declared_size'] for z in ranges.values())
 report=dict(real_critical=a.real_critical,exact_compiled_critical_match_bytes=8 if a.real_critical else 0,status='PASS',case_count=len(results),cases=results,ranges=ranges,elf_sha256=sha(elf),firmware_sha256=sha(blob),verifier_sha256=sha(Path(__file__).read_bytes()),source_manifest={str(f.relative_to(ROOT)):sha(f.read_bytes()) for f in sorted(Path(__file__).resolve().parents[1].rglob('*')) if f.suffix in ['.c','.h','.ld']},limits='Only critical-enter 0x473940 and delay 0x4807a0 intercepted on BOTH sides; no CQ function stub. Synthetic MMIO and serialized states, no concurrency/elapsed delay/real interrupt masking proof. Local caller and separate global slot fixtures, no stock handle-initialization proof.')
 if a.real_critical:report['limits']='Only delay0x4807a0 intercepted on BOTH sides; actual MRS/CPSID and PRIMASK restore execute in privileged serialized Unicorn state. Protected CQ index/address reads occur with PRIMASK1, prior mask restored. No actual interrupt delivery, scheduler interleavings, unprivileged enforcement, wall-clock or ROM timing proof.'
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(results),'fresh cases',ranges)
if __name__=='__main__':main()
