#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""IOM-like disable/term/uninitialize consumer with real CMDQ/PRIMASK; no stubs."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=0x438000
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/foundation/touch_scb/simulator/verify.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
H,Q,T,R,BUF,STOP=0x20001000,0x20003000,0x20004000,0x40050000,0x20008000,0x8000000
FUN={'term':(0x55c11a,32,'opencfw_iom_cq_term'),'disable':(0x55c430,104,'opencfw_iom_disable'),'uninitialize':(0x55c286,54,'opencfw_iom_uninitialize')}
w=lambda v:struct.pack('<I',v&0xffffffff)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def initial(c):
 h=bytearray(b'\xa5'*0x830)
 for off,v in [(0,c['prefix']),(4,c['module']),(0x24,c['pending']),(0x828,0 if c['qnull'] else Q)]:struct.pack_into('<I',h,off,v)
 q=bytearray(b''.join(w(v) for v in [c['qpfx'],BUF,BUF+256,0xdeadbeef,BUF+64,BUF+96,64,0,c['end'],T,0xaabbccdd]))
 return h,q

def run(segments,entry,c,entries):
 import unicorn as u
 import unicorn.arm_const as a
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4);pages=set()
 for s in segments:
  for p in range(s['address']&~4095,(s['address']+s['memory_size']+4095)&~4095,4096):
   if p not in pages:cpu.mem_map(p,4096);pages.add(p)
  cpu.mem_write(s['address'],s['data'])
 for low,n in [(0x20000000,0x10000),(R,0x8000),(STOP,4096)]:
  for p in range(low,low+n,4096):
   if p not in pages:cpu.mem_map(p,4096);pages.add(p)
 h,q=initial(c);cpu.mem_write(H-8,b'\xcc'*8+h+b'\xcc'*8);cpu.mem_write(Q-8,b'\xcc'*8+q+b'\xcc'*8);cpu.mem_write(BUF,b'\x5a'*256)
 reg=R+c['module']*4096
 cpu.mem_write(reg+0x11c,w(c['iomcfg']));cpu.mem_write(T,b''.join(w(v) for v in [reg+0x280,reg+0x284,reg+0x288,reg+0x28c,reg+0x290,c['pausemask']]))
 cpu.mem_write(reg+0x280,b''.join(w(v) for v in [c['cqcfg'],BUF+128,c['hw'],0,c['pause']]))
 trace={};mmio=[];writes=[];calls=[]
 def code(uc,pc,size,_):
  if pc in entries.values():
   name=next(k for k,v in entries.items() if v==pc);calls.append([name,uc.reg_read(a.UC_ARM_REG_R0),uc.reg_read(a.UC_ARM_REG_R1)&255 if name=='cmdq_term' else None,uc.reg_read(a.UC_ARM_REG_PRIMASK)])
  seg=next((s for s in segments if s['flags']&1 and s['address']<=pc<pc+size<=s['address']+len(s['data'])),None);assert seg is not None,hex(pc)
  raw=bytes(uc.mem_read(pc,size));assert raw==seg['data'][pc-seg['address']:pc-seg['address']+size];trace[pc]=raw.hex()
 def mem(uc,access,address,size,value,_):
  mask=uc.reg_read(a.UC_ARM_REG_PRIMASK)
  if R<=address<R+0x8000:
   assert size==4;mmio.append(['r' if access==u.UC_MEM_READ else 'w',address,struct.unpack('<I',uc.mem_read(address,4))[0] if access==u.UC_MEM_READ else value,mask])
  elif access==u.UC_MEM_WRITE and (H<=address<H+len(h) or Q<=address<Q+len(q)):
   assert size==4;writes.append([address,value&0xffffffff,mask])
 cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem)
 for regid,val in [(a.UC_ARM_REG_R0,0 if c['null'] else H),(a.UC_ARM_REG_R1,0),(a.UC_ARM_REG_SP,0x2000f000),(a.UC_ARM_REG_LR,STOP|1),(a.UC_ARM_REG_PRIMASK,c['prior'])]:cpu.reg_write(regid,val)
 saved={getattr(a,'UC_ARM_REG_R'+str(i)):0xabba0000+i for i in range(4,12)}
 for regid,val in saved.items():cpu.reg_write(regid,val)
 cpu.emu_start(entry|1,STOP,count=1000);assert cpu.reg_read(a.UC_ARM_REG_PC)==STOP and cpu.reg_read(a.UC_ARM_REG_SP)==0x2000f000;assert all(cpu.reg_read(r)==v for r,v in saved.items())
 for addr,n in [(H,len(h)),(Q,len(q))]:assert bytes(cpu.mem_read(addr-8,8))==bytes(cpu.mem_read(addr+n,8))==b'\xcc'*8
 assert bytes(cpu.mem_read(BUF,256))==b'\x5a'*256
 return dict(status=cpu.reg_read(a.UC_ARM_REG_R0),handle=bytes(cpu.mem_read(H,len(h))).hex(),queue=bytes(cpu.mem_read(Q,len(q))).hex(),iomcfg=bytes(cpu.mem_read(reg+0x11c,4)).hex(),cqregs=bytes(cpu.mem_read(reg+0x280,20)).hex(),primask=cpu.reg_read(a.UC_ARM_REG_PRIMASK),mmio=mmio,writes=writes,calls=calls,trace=trace)

def expected(c):
 h,q=initial(c);reg=R+c['module']*4096;cfg=c['iomcfg'];cq=c['cqcfg'];pause=c['pause'];mmio=[];writes=[];calls=[]
 def put(a,v,mask):
  writes.append([a,v&0xffffffff,mask]);struct.pack_into('<I',h if H<=a<H+len(h) else q,a-H if H<=a<H+len(h) else a-Q,v&0xffffffff)
 def rw(addr,value,nextvalue):mmio.extend([['r',addr,value,c['prior']],['w',addr,nextvalue,c['prior']]])
 def term():
  nonlocal cq,pause
  if not c['qnull']:
   calls.append(['cmdq_term',Q,1,c['prior']])
   if c['qpfx']&0x1ffffff==0x1cdcdcd:
    calls.append(['critical',None,None,c['prior']])
    mmio.extend([['r',reg+0x288,c['hw'],1],['r',reg+0x284,BUF+128,1]])
    idx=(c['end']&~255)|(c['hw']&255)
    if (c['end']-idx)&0x80000000:idx=(idx-256)&0xffffffff
    put(Q+0x1c,idx,1);put(Q+0xc,BUF+128,1);put(Q,c['qpfx']&~0x1000000,c['prior'])
    new=cq&~1;rw(reg+0x280,cq,new);cq=new
    new=pause&~c['pausemask']&0xffffffff;rw(reg+0x290,pause,new);pause=new
   put(H+0x828,0,c['prior'])
  return 0
 def disable():
  nonlocal cfg
  if c['null'] or c['prefix']&0x1ffffff!=0x1123456:return 2
  if not c['prefix']&0x2000000:return 0
  if c['pending']:return 3
  new=cfg&~1;rw(reg+0x11c,cfg,new);cfg=new
  new=cfg&~0x10;rw(reg+0x11c,cfg,new);cfg=new
  calls.append(['term',H,None,c['prior']]);term();put(H,c['prefix']&~0x2000000,c['prior']);return 0
 if c['op']=='term':status=term()
 elif c['op']=='disable':status=disable()
 elif c['null'] or c['prefix']&0x1ffffff!=0x1123456:status=2
 else:
  if c['prefix']&0x2000000:calls.append(['disable',H,None,c['prior']]);disable()
  put(H,struct.unpack_from('<I',h)[0]&~0x1000000,c['prior']);status=0
 return dict(status=status,handle=h.hex(),queue=q.hex(),iomcfg=w(cfg).hex(),cqregs=b''.join(w(v) for v in [cq,BUF+128,c['hw'],0,pause]).hex(),primask=c['prior'],mmio=mmio,writes=writes,calls=calls)

def cases():
 d=dict(prefix=0x3123456,module=0,pending=0,qpfx=0x3cdcdcd,qnull=False,end=0x102,hw=2,pausemask=0x100,iomcfg=0xffffffff,cqcfg=0x80000001,pause=0xf1234567,null=False,prior=0)
 variants=[{},dict(prefix=0x1123456),dict(prefix=0x2123456),dict(prefix=0x3123457),dict(prefix=0xff123456),dict(null=True),dict(pending=1),dict(pending=0xffffffff),dict(qnull=True),dict(qpfx=0x3cdcdce),dict(qpfx=0x2cdcdcd),dict(hw=1),dict(hw=255),dict(hw=0xffffff02),dict(end=0xffffffff,hw=0),dict(pausemask=0),dict(pausemask=0xffffffff),dict(iomcfg=0),dict(cqcfg=0x80000000)]
 for op in FUN:
  for module in [0,1,7]:
   for prior in [0,1]:
    for v in variants:
     c=dict(d,op=op,module=module,prior=prior);c.update(v)
     if op=='term' and c['null']:continue
     yield c

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();blob=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob.read_bytes()[32:]
 stock=[dict(address=p,memory_size=n,data=raw[p-BASE:p-BASE+n],flags=5) for p,n in [(0x55c000,4096),(0x538000,8192),(0x473000,4096)]]
 _,segments,syms=elf.elf_info(a.elf);results=[];observed={}
 se={'term':0x55c11a,'disable':0x55c430,'cmdq_term':0x53909a,'critical':0x473940};ce={'term':syms['opencfw_iom_cq_term']&~1,'disable':syms['opencfw_iom_disable']&~1,'cmdq_term':syms['am_hal_cmdq_term']&~1,'critical':syms['opencfw_cmdq_critical_enter']&~1}
 for c in cases():
  pc,n,symbol=FUN[c['op']];x=run(stock,pc,c,se);y=run(segments,syms[symbol]&~1,c,ce);trace=x.pop('trace');y.pop('trace')
  for r in [x,y]:
   r['calls']=[z for z in r['calls'] if z[0]!=c['op']]
   for z in r['calls']:
    if z[0]=='critical':z[1]=None
  assert x==y,(c,x,y);assert x==expected(c),(c,x,expected(c))
  for address,b in trace.items():assert address not in observed or observed[address]==b;observed[address]=b
  results.append(dict(inputs=c,result=x))
 tracebytes={a+i for a,b in observed.items() for i in range(len(bytes.fromhex(b)))}
 for pc,n,symbol in FUN.values():assert set(range(pc,pc+n))<=tracebytes,(symbol,n)
 manifest={str(p.relative_to(ROOT)):sha(p) for root in [ROOT/'g2/components/foundation/radio_iom_release',ROOT/'g2/components/foundation/ambiq_mspi'] for p in root.rglob('*') if p.suffix in ['.c','.h','.py','.ld']}
 report=dict(status='PASS',cases=len(results),results=results,original_trace={hex(a):b for a,b in sorted(observed.items())},unique_original_trace_bytes=len(tracebytes),source_manifest=manifest,elf_sha256=sha(a.elf),firmware_sha256=sha(blob),limits='Actual local IOM-like consumers, existing unchanged CMDQ term/index provider and real PRIMASK, no executable stubs. Synchronous nonaliasing mapped states, synthetic MMIO, buffer sentinel unchanged. No initializer/allocator/free/callback/interrupt/DMA scheduling/drain or complete transport-release proof; helper SDK attribution remains inferred.')
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(results),len(tracebytes))
if __name__=='__main__':main()
