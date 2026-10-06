#!/usr/bin/env python3
"""Actual service/callees and ISR notification boundary; synthetic raw registers."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('audio',ROOT/'g2/components/foundation/audio_cache_handoff/verify.py');audio=importlib.util.module_from_spec(spec);spec.loader.exec_module(audio)
cache=audio.cache
H,OUT,CELL,REG=0x20002000,0x20003000,0x2007450c,0x40208000
STOCK={'service':0x5908a0,'error':0x590cf4,'ipb':0x5909b6,'status':0x590848,'clear':0x590818,'irq':0x57a4d8,'get':0x57a7e0}
SOURCE={'service':'opencfw_i2s_interrupt_service','error':'opencfw_i2s_dma_error','ipb':'opencfw_i2s_ipb_service','status':'opencfw_i2s_interrupt_status','clear':'opencfw_i2s_interrupt_clear','irq':'opencfw_audio_i2s_irq_prefix','get':'opencfw_audio_rx_buffer_get'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

class Model:
 def __init__(self,c):
  self.h={0:c['magic'],4:c['module'],0x3c:0x20008000,0x40:c['pong'],0x44:0x2000a000,0x48:c['txpong'],0x4c:c['selected'],0x50:c['txselected'],0x54:c['length'],0x58:c['txlength']}
  self.reg={off:(0x5a5a0000 ^ off) for off in range(0,0x400,4)}
  self.reg.update({0x200:0xa55a0303,0x20c:c['rxstat'],0x218:c['txstat'],0x21c:c['next'],0x4c:c['ipb'],0x304:c['status'],0x300:c['enable']})
  self.events=[];self.out=b'\xa5'*8;self.base=REG+(c['module']<<12);self.ccr=c['ccr'];self.clear_effect=c['clear_effect']
 def read(self,off):self.events.append(['read',self.base+off,self.reg[off]]);return self.reg[off]
 def write(self,off,value):
  value&=0xffffffff;self.events.append(['write',self.base+off,value]);self.reg[off]=value
  if off==0x308 and self.clear_effect:self.reg[0x304]&=~value
 def error(self,d):
  self.write(0x200,0)
  if d&255==0:self.write(0x20c,0)
  elif d&255==1:self.write(0x218,0)
  return 0
 def ipb(self):
  initial=self.read(0x4c)
  for mask in [0x80000,0x20000,0x40000,0x10000]:
   if initial&mask:self.write(0x4c,self.read(0x4c)&~mask)
  return 0
 def service(self,status):
  if self.read(0x218)&4:self.error(1)
  if self.read(0x20c)&4:self.error(0)
  for bit,pong,selected,ping,length,stat,mask,addr,count in [(16,0x40,0x4c,0x3c,0x54,0x20c,1,0x224,0x220),(8,0x48,0x50,0x44,0x58,0x218,2,0x22c,0x228)]:
   if status&bit and self.h[pong]!=0xffffffff:
    self.write(stat,self.read(stat)&~2)
    if self.read(0x21c)&mask:return 9
    pointer=self.h[ping] if self.h[selected]==self.h[pong] else self.h[pong]
    self.h[selected]=pointer;self.events.append(['slot',selected,pointer]);self.write(addr,pointer);self.write(count,self.h[length]>>2);self.write(0x21c,self.read(0x21c)|mask)
  if status&1:self.ipb()
  return 0
 def status(self,enabled):
  if self.h[0]&0x01ffffff!=0x01125125:return 2
  value=self.read(0x304)
  if self.public_status:self.events.append(['status_store',OUT,value])
  if enabled&255:
   value&=self.read(0x300)
   if self.public_status:self.events.append(['status_store',OUT,value])
  self.out=struct.pack('<I',value)+self.out[4:];return 0
 def clear(self,status):
  if self.h[0]&0x01ffffff!=0x01125125:return 2
  self.write(0x308,status);self.read(0x304);return 0
 def get(self):
  self.events.append(['cell',H]);pointer=self.h[0x3c] if self.h[0x40]==0xffffffff else self.h[0x4c]
  e=cache.model(dict(ccr=self.ccr,null=False,clean=False,flag=0,size=2,address=pointer,length=3200))
  self.events.extend(x for x in e if not(x[0]=='read' and cache.H<=x[1]<cache.H+8))
  self.events.extend([['publish',OUT,pointer],['publish',OUT+4,3200]]);self.out=struct.pack('<II',pointer,3200);return pointer
 def invoke(self,kind,arg):
  self.events=[];self.public_status=kind=='status'
  if kind=='get':result=self.get()
  elif kind=='irq':
   self.events.append(['cell',H]);self.status(1);captured=int.from_bytes(self.out[:4],'little')
   self.events.append(['cell',H]);self.clear(captured);self.events.append(['cell',H]);self.service(captured)
   if captured&16:self.events.append(['notify_boundary',0x53c6b2])
   result=captured
   # Status helper's stack output is not the public OUT fixture.
   self.out=self.previous_out
  elif kind=='status':result=self.status(arg)
  elif kind=='clear':result=self.clear(arg)
  elif kind=='ipb':result=self.ipb()
  elif kind=='error':result=self.error(arg)
  else:result=self.service(arg)
  return result

class Machine:
 def __init__(self,segments,c,source,symbols=None):
  import unicorn as u;import unicorn.arm_const as a
  self.u=u;self.a=a;self.cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4);self.source=source;self.symbols=symbols;self.c=c;self.base=REG+(c['module']<<12);self.events=[];self.trace={};self.notify=False
  cpu=self.cpu;pages=set()
  for s in segments:
   for p in range(s['address']&~4095,(s['address']+s['memory_size']+4095)&~4095,4096):
    if p not in pages:cpu.mem_map(p,4096);pages.add(p)
   cpu.mem_write(s['address'],s['data'])
  for start,n in [(0x20000000,0x10000),(0x20074000,4096),(REG,8192),(0xe000e000,8192),(cache.STOP,4096)]:cpu.mem_map(start,n)
  model=Model(c);self.initial=bytearray(b'\xa5'*0x80)
  for off,value in model.h.items():struct.pack_into('<I',self.initial,off,value)
  cpu.mem_write(H-8,b'\xcc'*8+self.initial+b'\xcc'*8);cpu.mem_write(OUT-8,b'\xcc'*8+b'\xa5'*8+b'\xcc'*8);cpu.mem_write(CELL,struct.pack('<I',H))
  for off,value in model.reg.items():cpu.mem_write(self.base+off,struct.pack('<I',value))
  cpu.mem_write(cache.CCR,struct.pack('<I',c['ccr']));cpu.mem_write(cache.SIZE,struct.pack('<I',2));cpu.mem_write(0x20008000,b'\x5a'*512)
  self.segments=segments;cpu.hook_add(u.UC_HOOK_CODE,self.code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,self.memory)
 def code(self,uc,pc,size,_):
  if pc==cache.STOP:uc.emu_stop();return
  if not self.source and pc==0x53c6b2:
   self.notify=True;self.events.append(['notify_boundary',pc]);uc.emu_stop();return
  s=next((s for s in self.segments if s['flags']&1 and s['address']<=pc and pc+size<=s['address']+len(s['data'])),None);assert s is not None,hex(pc)
  raw=bytes(uc.mem_read(pc,size));assert raw==s['data'][pc-s['address']:pc-s['address']+size];self.trace[hex(pc)]=raw.hex()
  if raw==bytes.fromhex('bff34f8f'):self.events.append(['dsb'])
  if raw==bytes.fromhex('bff36f8f'):self.events.append(['isb'])
 def memory(self,uc,access,at,size,value,_):
  u=self.u
  if self.base<=at<self.base+0x400 or 0xe000e000<=at<0xe0010000:
   assert size==4;v=struct.unpack('<I',uc.mem_read(at,4))[0] if access==u.UC_MEM_READ else value&0xffffffff;self.events.append(['read' if access==u.UC_MEM_READ else 'write',at,v])
   if access==u.UC_MEM_WRITE and at==self.base+0x308 and self.c['clear_effect']:
    old=struct.unpack('<I',uc.mem_read(self.base+0x304,4))[0];uc.mem_write(self.base+0x304,struct.pack('<I',old&~v))
  elif access==u.UC_MEM_WRITE and H<=at<H+0x80:
   assert at-H in [0x4c,0x50] and size==4;self.events.append(['slot',at-H,value&0xffffffff])
  elif at==CELL:
   assert access==u.UC_MEM_READ and size==4;self.events.append(['cell',struct.unpack('<I',uc.mem_read(at,4))[0]])
  elif access==u.UC_MEM_WRITE and OUT<=at<OUT+8 and self.kind in ['get','status']:self.events.append(['publish' if self.kind=='get' else 'status_store',at,value&0xffffffff])
 def invoke(self,kind,arg):
  cpu,a=self.cpu,self.a;self.kind=kind;self.events=[];self.notify=False
  entry=(self.symbols[SOURCE[kind]]&~1) if self.source else STOCK[kind]
  args=[H,arg,0,0]
  if kind=='status':args=[H,OUT,arg,0]
  elif kind=='get':args=[OUT,OUT+4,0,0]
  for reg,v in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3],args):cpu.reg_write(reg,v)
  cpu.reg_write(a.UC_ARM_REG_SP,cache.SP);cpu.reg_write(a.UC_ARM_REG_LR,cache.STOP|1);cpu.reg_write(a.UC_ARM_REG_PRIMASK,self.c['prior'])
  context=60 if kind=='irq' else 0 if kind=='get' else 60 if self.c['prior'] else 0
  cpu.reg_write(a.UC_ARM_REG_IPSR,context);assert cpu.reg_read(a.UC_ARM_REG_IPSR)==context
  saved={getattr(a,'UC_ARM_REG_R'+str(i)):0xabba0000+i for i in range(4,12)}
  for reg,v in saved.items():cpu.reg_write(reg,v)
  cpu.emu_start(entry|1,cache.STOP,count=10000)
  if self.notify:
   assert kind=='irq';status=struct.unpack('<I',cpu.mem_read(cpu.reg_read(a.UC_ARM_REG_SP),4))[0];cut='before actual notifier, live ISR stack; ABI return not claimed'
  else:
   assert cpu.reg_read(a.UC_ARM_REG_PC)==cache.STOP and cpu.reg_read(a.UC_ARM_REG_SP)==cache.SP;assert all(cpu.reg_read(r)==v for r,v in saved.items());status=cpu.reg_read(a.UC_ARM_REG_R0);cut='complete function return'
   if kind=='irq' and status&16:self.events.append(['notify_boundary',0x53c6b2])
  assert cpu.reg_read(a.UC_ARM_REG_IPSR)==context;assert cpu.reg_read(a.UC_ARM_REG_PRIMASK)==self.c['prior'];assert bytes(cpu.mem_read(H-8,8))==bytes(cpu.mem_read(H+0x80,8))==b'\xcc'*8;assert bytes(cpu.mem_read(OUT-8,8))==bytes(cpu.mem_read(OUT+8,8))==b'\xcc'*8;assert bytes(cpu.mem_read(0x20008000,512))==b'\x5a'*512
  return dict(status=status,events=self.events,handle=bytes(cpu.mem_read(H,0x80)).hex(),registers=bytes(cpu.mem_read(self.base,0x400)).hex(),output=bytes(cpu.mem_read(OUT,8)).hex(),endpoint=cut)
 def set_next(self,value):self.cpu.mem_write(self.base+0x21c,struct.pack('<I',value))

def check(c,m,result,status):
 assert result['status']==status,(c,'status',result,status)
 assert result['events']==m.events,(c,'events',result['events'],m.events)
 expected=bytearray(b'\xa5'*0x80)
 for off,v in m.h.items():struct.pack_into('<I',expected,off,v)
 assert result['handle']==expected.hex();assert result['output']==m.out.hex()
 assert result['registers']==b''.join(struct.pack('<I',m.reg[off]) for off in range(0,0x400,4)).hex()

def cases():
 d=dict(module=0,magic=0x01125125,pong=0x20009000,txpong=0x2000b000,selected=0x20008000,txselected=0x2000a000,length=3200,txlength=3203,rxstat=0x80000003,txstat=0x40000003,next=0xa55a0000,ipb=0xdeadffff,status=16,enable=0xffffffff,prior=0,ccr=0x10000,clear_effect=False)
 for status,nextbits,errors,pongs,prior in itertools.product([0,1,8,16,24,25],[0,1,2,3],[0,1,2,3],[0,1,2],[0,1]):
  yield dict(d,kind='service',arg=status,next=d['next']|nextbits,rxstat=d['rxstat']|(4 if errors&1 else 0),txstat=d['txstat']|(4 if errors&2 else 0),pong=0xffffffff if pongs==1 else d['pong'],txpong=0xffffffff if pongs==2 else d['txpong'],prior=prior)
 for txlength in [0,1,3200,3203,0xffffffff]:
  yield dict(d,kind='service',arg=25,txselected=d['txpong'],txlength=txlength,module=1,prior=1)
 for kind in ['error','status','clear','ipb']:
  for module,arg,valid in itertools.product([0,1],[0,1,255,256,257,0xffffffff],[True,False]):
   yield dict(d,kind=kind,arg=arg,module=module,magic=d['magic'] if valid else 0x125125,ipb=0xdeadffff ^ ((arg&15)<<16))
 for status,enable,nextbits,effect in itertools.product([0,1,8,16,24,25],[0,8,16,25],[0,1,2,3],[False,True]):
  yield dict(d,kind='irq',arg=0,status=status,enable=enable,next=d['next']|nextbits,clear_effect=effect)
 for initial,length in itertools.product([0x20008000,0x20009000,0x2000c000],[0,1,3200,3203,0xffffffff]):
  yield dict(d,kind='sequence',arg=16,selected=initial,length=length)
  yield dict(d,kind='irqsequence',arg=16,selected=initial,length=length)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 blob=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob.read_bytes()[32:]
 stock=[dict(address=p,memory_size=n,data=raw[p-cache.BASE:p-cache.BASE+n],flags=f) for p,n,f in [(0x475000,4096,5),(0x57a000,4096,5),(0x590000,8192,5),(0x78d000,4096,4),(0x53c000,4096,5)]]
 _,segments,symbols=cache.elf_reader.elf_info(args.elf);results=[];trace={};operations=0
 for c in cases():
  m=Model(c);original=Machine(stock,c,False);source=Machine(segments,c,True,symbols);steps=[]
  sequence=[('irq' if c['kind']=='irqsequence' else 'service',16),('get',0),('advance_next_slot',c['next']),('irq' if c['kind']=='irqsequence' else 'service',16),('get',0),('irq' if c['kind']=='irqsequence' else 'service',16)] if c['kind'] in ['sequence','irqsequence'] else [(c['kind'],c['arg'])]
  for kind,arg in sequence:
   if kind=='advance_next_slot':m.reg[0x21c]=arg;original.set_next(arg);source.set_next(arg);steps.append(dict(synthetic_external_step='next-slot bit cleared between calls, not actual hardware trace'));continue
   m.previous_out=m.out;status=m.invoke(kind,arg);o=original.invoke(kind,arg);s=source.invoke(kind,arg);check(c,m,o,status);check(c,m,s,status)
   assert {k:v for k,v in o.items() if k!='endpoint'}=={k:v for k,v in s.items() if k!='endpoint'};steps.append(dict(kind=kind,arg=arg,original=o,source=s));operations+=1
  for pc,value in original.trace.items():assert pc not in trace or trace[pc]==value;trace[pc]=value
  results.append(dict(inputs=c,steps=steps))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 result=dict(status='PASS',cases=len(results),invocations=operations,results=results,original_trace=trace,unique_original_trace_bytes=len(used),firmware_sha256=sha(blob),elf_sha256=sha(args.elf),source_manifest={str(p.relative_to(ROOT)):sha(p) for component in ['audio_dma_rearm','audio_cache_handoff','cache_maintenance'] for p in (ROOT/'g2/components/foundation'/component).iterdir() if p.suffix in ['.c','.h','.py']},limits='Real service/error/IPB/status/clear/query/getter/cache instructions, no executable callee stubs. ISR stops before actual notifier53c6b2 with live stack; source prefix returns capturedstatus, not full ISR or actual queue delivery. Raw synthetic MMIO; optional INTCLR effect, IPSR60/0 fixture context and next-slot advance explicit synthetic events, not actual scheduling. No physical cache/DMA/lifetime proof. Huge cache prefixes/ROM timing/O2 tick remain separate.')
 with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print('PASS',result['cases'],'scenarios',operations,'calls',len(used),'trace bytes')
if __name__=='__main__':main()
