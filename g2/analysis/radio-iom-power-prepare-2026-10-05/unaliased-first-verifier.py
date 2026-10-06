#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fixed power-operation2 preparation and disable→prepare, exact external cut."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=0x438000
spec=importlib.util.spec_from_file_location('prev',ROOT/'g2/components/foundation/radio_iom_release/verify.py');prev=importlib.util.module_from_spec(spec);spec.loader.exec_module(prev)
elf=prev.elf;H,Q,T,R,BUF,STOP=prev.H,prev.Q,prev.T,prev.R,prev.BUF,prev.STOP
w=prev.w;sha=prev.sha
SAVES={0x104:0x86c,0x118:0x874,0x11c:0x878,0x228:0x87c,0x22c:0x880,0x234:0x884,0x23c:0x888,0x240:0x88c,0x244:0x890,0x280:0x894,0x2c0:0x898,0x200:0x89c,0x210:0x870}
def initial(c):
 h,q=prev.initial(c);h.extend(b'\xa5'*(0x8a0-len(h)));h[0x868]=c['retained_flag'];return h,q
def run(segments,entry,c,entries,stock=False):
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
 
 for off in SAVES:cpu.mem_write(reg+off,w(c['seed']^(off*0x101)))
 cpu.mem_write(reg+0x228,w(c['active']));cpu.mem_write(reg+0x248,w(c['ready']));cpu.mem_write(reg+0x11c,w(c['iomcfg']));cpu.mem_write(T,b''.join(w(v) for v in [reg+0x280,reg+0x284,reg+0x288,reg+0x28c,reg+0x290,c['pausemask']]))
 cpu.mem_write(reg+0x280,b''.join(w(v) for v in [c['cqcfg'],BUF+128,c['hw'],0,c['pause']]))
 trace={};mmio=[];writes=[];calls=[]
 def code(uc,pc,size,_):
  if stock and pc==STOP:uc.emu_stop();return # synthetic caller-return endpoint; no guest instruction executed
  if pc in entries.values():
   name=next(k for k,v in entries.items() if v==pc);calls.append([name,uc.reg_read(a.UC_ARM_REG_R0),uc.reg_read(a.UC_ARM_REG_PRIMASK)])
  seg=next((s for s in segments if s['flags']&1 and s['address']<=pc<pc+size<=s['address']+len(s['data'])),None);assert seg is not None,hex(pc)
  raw=bytes(uc.mem_read(pc,size));assert raw==seg['data'][pc-seg['address']:pc-seg['address']+size];trace[pc]=raw.hex()
 def mem(uc,access,address,size,value,_):
  mask=uc.reg_read(a.UC_ARM_REG_PRIMASK)
  if R<=address<R+0x8000:
   assert size==4;mmio.append(['r' if access==u.UC_MEM_READ else 'w',address,struct.unpack('<I',uc.mem_read(address,4))[0] if access==u.UC_MEM_READ else value,mask])
  elif access==u.UC_MEM_WRITE and (H<=address<H+len(h) or Q<=address<Q+len(q)):
   assert size in [1,4];writes.append([address,size,value&((1<<(8*size))-1),mask])
 cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem)
 for regid,val in [(a.UC_ARM_REG_R0,0 if c['null'] else H),(a.UC_ARM_REG_R1,2 if stock else c['retention']),(a.UC_ARM_REG_R2,c['retention']),(a.UC_ARM_REG_SP,0x2000f000),(a.UC_ARM_REG_LR,STOP|1),(a.UC_ARM_REG_PRIMASK,c['prior'])]:cpu.reg_write(regid,val)
 saved={getattr(a,'UC_ARM_REG_R'+str(i)):0xabba0000+i for i in range(4,12)}
 for regid,val in saved.items():cpu.reg_write(regid,val)
 if stock and c['op']=='sequence':
  cpu.reg_write(a.UC_ARM_REG_R0,0 if c['null'] else H);cpu.reg_write(a.UC_ARM_REG_R1,0)
  cpu.emu_start(0x55c430|1,STOP,count=1000);assert cpu.reg_read(a.UC_ARM_REG_PC)==STOP and cpu.reg_read(a.UC_ARM_REG_SP)==0x2000f000
  assert all(cpu.reg_read(r)==v for r,v in saved.items())
  cpu.reg_write(a.UC_ARM_REG_R0,0 if c['null'] else H);cpu.reg_write(a.UC_ARM_REG_R1,2);cpu.reg_write(a.UC_ARM_REG_R2,c['retention']);cpu.reg_write(a.UC_ARM_REG_LR,STOP|1)
 cpu.emu_start(entry|1,0x55ca72 if stock else STOP,count=3000)
 end=cpu.reg_read(a.UC_ARM_REG_PC);prepared=stock and end==0x55ca72
 assert end in ([STOP,0x55ca72] if stock else [STOP])
 assert cpu.reg_read(a.UC_ARM_REG_SP)==(0x2000eff0 if prepared else 0x2000f000)
 if prepared:
  assert cpu.reg_read(a.UC_ARM_REG_R4)==H and cpu.reg_read(a.UC_ARM_REG_R5)==c['retention']&255
 else:assert all(cpu.reg_read(r)==v for r,v in saved.items())

 for addr,n in [(H,len(h)),(Q,len(q))]:assert bytes(cpu.mem_read(addr-8,8))==bytes(cpu.mem_read(addr+n,8))==b'\xcc'*8
 assert bytes(cpu.mem_read(BUF,256))==b'\x5a'*256
 return dict(status=0 if prepared else cpu.reg_read(a.UC_ARM_REG_R0),handle=bytes(cpu.mem_read(H,len(h))).hex(),queue=bytes(cpu.mem_read(Q,len(q))).hex(),iomcfg=bytes(cpu.mem_read(reg+0x11c,4)).hex(),cqregs=bytes(cpu.mem_read(reg+0x280,20)).hex(),primask=cpu.reg_read(a.UC_ARM_REG_PRIMASK),mmio=mmio,writes=writes,calls=calls,trace=trace)
def expected(c):
 h,q=initial(c);reg=R+c['module']*4096;cfg=c['iomcfg'];cq=c['cqcfg'];pause=c['pause'];mmio=[];writes=[];calls=[]
 if c['op']=='sequence':
  d=prev.expected(dict(c,op='disable'));h[:0x830]=bytes.fromhex(d['handle']);q=bytearray.fromhex(d['queue']);cfg=struct.unpack('<I',bytes.fromhex(d['iomcfg']))[0];cq=struct.unpack('<I',bytes.fromhex(d['cqregs'])[:4])[0];pause=struct.unpack('<I',bytes.fromhex(d['cqregs'])[16:20])[0]
  mmio=d['mmio'];writes=[[a,4,v,m] for a,v,m in d['writes']];calls=[['disable',0 if c['null'] else H,c['prior']]]+[[z[0],z[1],z[3]] for z in d['calls']]
 prefix=struct.unpack_from('<I',h)[0]
 def put(a,size,v):
  writes.append([a,size,v,c['prior']]);buf=h if H<=a<H+len(h) else q;off=a-H if buf is h else a-Q;buf[off:off+size]=v.to_bytes(size,'little')
 if c['null'] or prefix&0x1ffffff!=0x1123456:status=2
 else:
  busy=False
  if prefix&0x2000000:
   mmio.append(['r',reg+0x248,c['ready'],c['prior']]);busy=(c['ready']&6)!=4 or bool(c['pending'])
  if busy:status=3
  else:
   if c['retention']&255:
    for off,dst in SAVES.items():
     value=cfg if off==0x11c else cq if off==0x280 else c['active'] if off==0x228 else c['seed']^(off*0x101)
     mmio.append(['r',reg+off,value,c['prior']]);put(H+dst,4,value)
    mmio.append(['r',reg+0x228,c['active'],c['prior']])
    if c['active']&1:
     ptr=struct.unpack_from('<I',h,0x828)[0];calls.extend([['pause',H,c['prior']],['cq_disable',ptr,c['prior']]])
     qpfx=struct.unpack_from('<I',q)[0]
     if ptr and qpfx&0x1ffffff==0x1cdcdcd and qpfx&0x2000000:
      value=cq&~1;mmio.extend([['r',reg+0x280,cq,c['prior']],['w',reg+0x280,value,c['prior']]]);cq=value;put(Q,4,qpfx&~0x2000000)
    put(H+0x868,1,1)
   for bit in [1,0x10]:
    value=cfg&~bit;mmio.extend([['r',reg+0x11c,cfg,c['prior']],['w',reg+0x11c,value,c['prior']]]);cfg=value
   status=0
 return dict(status=status,handle=h.hex(),queue=q.hex(),iomcfg=w(cfg).hex(),cqregs=b''.join(w(v) for v in [cq,BUF+128,c['hw'],0,pause]).hex(),primask=c['prior'],mmio=mmio,writes=writes,calls=calls)

def cases():
 d=dict(prefix=0x3123456,module=0,pending=0,qpfx=0x3cdcdcd,qnull=False,end=0x102,hw=2,pausemask=0x100,iomcfg=0xffffffff,cqcfg=0x80000001,pause=0xf1234567,null=False,prior=0,retention=1,retained_flag=0,active=1,ready=4,seed=0xa1b2c3d4)
 variants=[{},dict(prefix=0x1123456),dict(prefix=0x3123457),dict(null=True),dict(pending=1),dict(qnull=True),dict(qpfx=0x3cdcdce),dict(qpfx=0x1cdcdcd),dict(active=0),dict(active=2),dict(retained_flag=255),dict(iomcfg=0),dict(cqcfg=0x80000000)]
 for op in ['prepare','sequence']:
  for module in [0,1,7]:
   for prior in [0,1]:
    for retention in [0,1,255,256,257]:
     for v in variants:
      c=dict(d,op=op,module=module,prior=prior,retention=retention);c.update(v);yield c
 for ready in range(8):
  for pending in [0,1]:
   for prior in [0,1]:yield dict(d,op='prepare',ready=ready,pending=pending,prior=prior)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();blob=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';raw=blob.read_bytes()[32:];assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
 stock=[dict(address=p,memory_size=n,data=raw[p-BASE:p-BASE+n],flags=5) for p,n in [(0x55c000,8192),(0x538000,8192),(0x473000,4096)]]
 _,segments,syms=elf.elf_info(a.elf);results=[];observed={}
 se={'disable':0x55c430,'term':0x55c11a,'pause':0x55c168,'cmdq_term':0x53909a,'cq_disable':0x538e8c,'critical':0x473940}
 ce={name:syms[symbol]&~1 for name,symbol in [('disable','opencfw_iom_disable'),('term','opencfw_iom_cq_term'),('pause','opencfw_iom_cq_pause'),('cmdq_term','am_hal_cmdq_term'),('cq_disable','am_hal_cmdq_disable'),('critical','opencfw_cmdq_critical_enter')]}
 for c in cases():
  symbol='opencfw_iom_powerdown_prepare' if c['op']=='prepare' else 'opencfw_iom_disable_then_prepare'
  x=run(stock,0x55c7e8,c,se,True);y=run(segments,syms[symbol]&~1,c,ce);trace=x.pop('trace');y.pop('trace')
  for r in [x,y]:
   for z in r['calls']:
    if z[0]=='critical':z[1]=None
  model=expected(c);assert x==y,(c,{k:(x[k],y[k]) for k in x if x[k]!=y[k]});assert x==model,(c,{k:(x[k],model[k]) for k in x if x[k]!=model[k]})
  for address,b in trace.items():assert address not in observed or observed[address]==b;observed[address]=b
  results.append(dict(inputs=c,result=x))
 used={a+i for a,b in observed.items() for i in range(len(bytes.fromhex(b)))}
 manifest={str(p.relative_to(ROOT)):sha(p) for root in [ROOT/'g2/components/foundation/radio_iom_power_prepare',ROOT/'g2/components/foundation/radio_iom_release',ROOT/'g2/components/foundation/ambiq_mspi'] for p in root.rglob('*') if p.suffix in ['.c','.h','.py','.ld']}
 report=dict(status='PASS',cases=len(results),results=results,original_trace={hex(a):b for a,b in sorted(observed.items())},unique_original_trace_bytes=len(used),source_manifest=manifest,elf_sha256=sha(a.elf),firmware_sha256=sha(blob),limits='Fixed power operation2 prefix only, success stops55ca72 before physical power callbacks; real early return2/3 paths execute. Source0 means prepared, not powered down. Sequence follows disable then prepare with no physical step/uninitialize. No stubs. Raw MMIO/serialized states; no timeout/callback/NVIC/DMA/free/quiescence proof. No closure of prior wrapped-index asynchronous ownership limitation; sequence cases use nonwrap hardware index.')
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(results),len(used))
if __name__=='__main__':main()
