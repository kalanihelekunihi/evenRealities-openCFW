#!/usr/bin/env python3
"""Execute authenticated notification/queue/consumer/dispatch bodies to explicit cuts."""
import argparse,hashlib,importlib.util,json,struct,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('rearm',ROOT/'g2/components/foundation/audio_dma_rearm/verify.py');rearm=importlib.util.module_from_spec(spec);spec.loader.exec_module(rearm)
cache=rearm.cache
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
Q,DATA,MSG,CUT,PCM,PONG,H=0x20004000,0x20005000,0x20006000,0x20007000,0x20008000,0x20009000,0x20002000
TABLE,TICK,COUNT=0x20073c20,0x20074a34,0x20074a9c
CALL,CALL2=0x08001001,0x08001101
STOCK={'notify':0x53c6b2,'consume':0x53c6f2,'dispatch':0x57adf8,'put':0x449abe,'get':0x449b3c,'service':0x5908a0,'context':0x44900e,'scheduler':0x4558a4}
SOURCE={'notify':'opencfw_audio_notify_prefix','consume':'opencfw_audio_consume_prefix','dispatch':'opencfw_pcm_dispatch_prefix','put':'opencfw_audio_queue_put_isr','get':'opencfw_audio_queue_get_task_nowait','service':'opencfw_i2s_interrupt_service','context':'opencfw_audio_irq_context','scheduler':'opencfw_audio_scheduler_state'}
class Machine:
 def __init__(self,segments,symbols=None):
  import unicorn as u,unicorn.arm_const as a
  self.u,self.a=u,a;self.source=symbols is not None;self.symbols=symbols or {};self.cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4)
  pages=set()
  for s in segments:
   for p in range(s['address']&~4095,(s['address']+s['memory_size']+4095)&~4095,4096):
    if p not in pages:self.cpu.mem_map(p,4096);pages.add(p)
   self.cpu.mem_write(s['address'],s['data'])
  for start,n in [(0x20000000,0x80000),(0x40208000,8192),(0xe000e000,8192),(0x08000000,0x3000),(0x455000,4096)]:
   for p in range(start,start+n,4096):
    if p not in pages:self.cpu.mem_map(p,4096);pages.add(p)
  self.segments=segments;self.trace={};self.cpu.hook_add(u.UC_HOOK_CODE,self.code);self.cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,self.memory)
  self.w(0x20003fa4,Q);self.w(0x20003fa0,0x20006600);self.w(0x20074a3c,1);self.w(0x20074a58,0);self.w(0x2007450c,H)
  for off,value in {0:0x01125125,4:0,0x3c:PCM,0x40:PONG,0x44:PCM,0x48:PONG,0x4c:PCM,0x50:PCM,0x54:3200,0x58:3200}.items():self.w(H+off,value)
  self.cpu.mem_write(PCM,b'\x11'*3200);self.cpu.mem_write(PONG,b'\x22'*3200)
  self.w(cache.CCR,0x10000);self.w(cache.SIZE,2);self.w(TABLE+8,CALL);self.cpu.mem_write(TABLE+4,b'\0');self.w(TABLE+20,CALL);self.cpu.mem_write(TABLE+16,b'\1')
  self.queue(3)
 def w(self,at,value):self.cpu.mem_write(at,struct.pack('<I',value&0xffffffff))
 def r(self,at):return struct.unpack('<I',self.cpu.mem_read(at,4))[0]
 def queue(self,capacity):
  self.cpu.mem_write(Q,b'\0'*80)
  for off,value in {0:DATA,4:DATA,8:DATA+12*capacity,12:DATA+12*(capacity-1),0x3c:capacity,0x40:12}.items():self.w(Q+off,value)
  self.cpu.mem_write(Q+0x44,b'\xff\xff');self.cpu.mem_write(DATA,b'\xa5'*(12*capacity))
 def code(self,uc,pc,size,_):
  if pc==cache.STOP:uc.emu_stop();return
  if self.source and pc in [0x455370,0x45596e,0x08002000]:raise AssertionError(('unimplemented provider reached',hex(pc)))
  if not self.source:
   if pc in [CALL&~1,CALL2&~1]:
    self.cut=dict(disposition=1,mode=uc.reg_read(self.a.UC_ARM_REG_R0),pcm=uc.reg_read(self.a.UC_ARM_REG_R1),length=uc.reg_read(self.a.UC_ARM_REG_R2),callback=pc|1);uc.emu_stop();return
   if pc==0x57ae56 and self.kind in ['consume','dispatch']:
    self.cut=dict(disposition=2,mode=0,pcm=uc.reg_read(self.a.UC_ARM_REG_R5),length=uc.reg_read(self.a.UC_ARM_REG_R4),callback=0);uc.emu_stop();return
   if pc==0x43d0ce:
    self.cut=dict(disposition=3 if self.kind=='consume' else 5);uc.emu_stop();return
   if pc==0x449238:
    assert uc.reg_read(self.a.UC_ARM_REG_R1)==0x400000
    self.cut=dict(disposition=4,callback=uc.reg_read(self.a.UC_ARM_REG_R0));uc.emu_stop();return
  s=next((s for s in self.segments if s['flags']&1 and s['address']<=pc< s['address']+len(s['data'])),None)
  assert s is not None,('unexpected execution',hex(pc))
  raw=bytes(uc.mem_read(pc,size));assert raw==s['data'][pc-s['address']:pc-s['address']+size];self.trace[hex(pc)]=raw.hex()
 def memory(self,uc,access,at,size,value,_):
  if access==self.u.UC_MEM_READ and at in [TABLE+8,TABLE+20]:
   self.callback_reads+=1
   if self.change_callback and self.callback_reads==2:self.w(at,CALL2)
  if access==self.u.UC_MEM_READ and (PCM<=at<PCM+3200 or PONG<=at<PONG+3200):self.pcm_reads+=1
  if access==self.u.UC_MEM_READ and at==TABLE+8 and self.change_pcm:
   uc.mem_write(PCM,b'\x33'*3200);uc.mem_write(PONG,b'\x44'*3200)
  if at==COUNT and access==self.u.UC_MEM_WRITE:self.events.append(['count',value&0xffffffff])
  if access==self.u.UC_MEM_WRITE and at==H+0x4c:self.events.append(['selected',value&0xffffffff])
  if access==self.u.UC_MEM_WRITE and at in [0xe000ef5c,0xe000ef70,0xe000ef68]:self.events.append(['cache',at,value&0xffffffff])
 def invoke(self,kind,args=(),change_callback=False,change_pcm=False,ipsr=None,primask=0,basepri=0):
  cpu,a=self.cpu,self.a;self.kind=kind;self.cut=None;self.events=[];self.callback_reads=0;self.pcm_reads=0;self.change_callback=change_callback;self.change_pcm=change_pcm
  self.cpu.mem_write(CUT,b'\0'*24)
  if self.source:
   argv={'notify':[CUT],'consume':[MSG,CUT],'dispatch':list(args)+[CUT],'put':[Q,MSG],'get':[Q,MSG],'service':[H,*args],'context':[],'scheduler':[]}[kind]
   entry=self.symbols[SOURCE[kind]]&~1
  else:
   argv={'notify':[],'consume':[MSG],'dispatch':list(args),'put':[Q,MSG,0,0],'get':[Q,MSG,0,0],'service':[H,*args],'context':[],'scheduler':[]}[kind];entry=STOCK[kind]
  for reg,value in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3],argv):cpu.reg_write(reg,value)
  for reg,value in [(a.UC_ARM_REG_SP,cache.SP),(a.UC_ARM_REG_LR,cache.STOP|1),(a.UC_ARM_REG_IPSR,ipsr if ipsr is not None else 60 if kind in ['put','notify','service'] else 0),(a.UC_ARM_REG_PRIMASK,primask),(a.UC_ARM_REG_BASEPRI,basepri)]:cpu.reg_write(reg,value)
  cpu.emu_start(entry|1,cache.STOP,count=30000)
  if self.source and kind in ['notify','consume','dispatch']:
   v=struct.unpack('<6I',cpu.mem_read(CUT,24));self.cut=dict(zip(['disposition','mode','pcm','length','callback','age'],v))
  if not self.cut:
   assert cpu.reg_read(a.UC_ARM_REG_PC)==cache.STOP and cpu.reg_read(a.UC_ARM_REG_SP)==cache.SP
   self.cut=dict(disposition=0) if kind in ['notify','consume','dispatch'] else dict(status=cpu.reg_read(a.UC_ARM_REG_R0))
  assert not self.pcm_reads,('PCM unexpectedly copied/read before callback/DSP cut',kind,self.pcm_reads)
  return dict(cut=self.cut,events=self.events,queue=bytes(cpu.mem_read(Q,80)).hex(),data=bytes(cpu.mem_read(DATA,36)).hex(),message=bytes(cpu.mem_read(MSG,12)).hex(),count=self.r(COUNT),selected=self.r(H+0x4c),basepri=cpu.reg_read(a.UC_ARM_REG_BASEPRI),nest=self.r(0x2000309c),pcm=bytes(cpu.mem_read(PCM,3200)).hex(),pong=bytes(cpu.mem_read(PONG,3200)).hex())
def compare(o,s):
 assert {k:v for k,v in o.items() if k!='cut'}=={k:v for k,v in s.items() if k!='cut'},('state',o,s)
 for k,v in o['cut'].items():assert s['cut'][k]==v,('cut',o['cut'],s['cut'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 blob=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';b=blob.read_bytes()[32:]
 stock=[dict(address=cache.BASE,memory_size=len(b),data=b,flags=5)];_,segments,symbols=cache.elf_reader.elf_info(args.elf)
 results=[];trace={};calls=0
 def pair():return Machine(stock),Machine(segments,symbols)
 def step(name,machines,kind,args=(),**kw):
  nonlocal calls
  o,s=[m.invoke(kind,args,**kw) for m in machines];compare(o,s);calls+=1;results.append(dict(name=name,kind=kind,args=args,fixture=kw,original=o,source=s));trace.update(machines[0].trace)
 # True stock wrapper context reads, scheduler and tick-age unsigned wrap.
 for running,suspended,ipsr,mask,pri in itertools.product([0,1],[0,1],[0,60],[0,1],[0,0x30]):
  pairm=pair()
  for m in pairm:m.w(0x20074a3c,running);m.w(0x20074a58,suspended)
  step('context',pairm,'context',ipsr=ipsr,primask=mask,basepri=pri)
 for now,age,callback in itertools.product([0,10,0xffffffff,0x80000000],[0,1,40,41,42,0x80000000,0xffffffff],[True,False]):
  ms=pair()
  for m in ms:m.w(TICK,now);m.w(MSG+8,now-age);m.w(TABLE+8,CALL if callback else 0);m.w(COUNT,0xffffffff)
  step('age_rollover',ms,'consume')
  assert ms[1].r(CUT)==(1 if callback else 2) if age<41 else ms[1].r(CUT)==3
 # Direct dispatch covers invalid inputs, low-byte modes and registration mismatch.
 for mode,ptr,length,regmode,callback in itertools.product([0,1,2,256,257,0xffffffff],[0,PCM],[0,3200],[0,1],[0,CALL]):
  ms=pair()
  for m in ms:
   m.w(TABLE+8,callback);m.w(TABLE+20,callback);m.cpu.mem_write(TABLE+4,bytes([regmode]));m.cpu.mem_write(TABLE+16,bytes([regmode]))
  step('dispatch_layout',ms,'dispatch',[mode,ptr,length])
 for change_callback,change_pcm in [(True,False),(False,True),(True,True)]:
  ms=pair()
  for m in ms:m.w(TICK,7);m.w(MSG+8,7)
  step('borrowed_change',ms,'consume',change_callback=change_callback,change_pcm=change_pcm)
 # Actual notifications queue copied timestamp only, FIFO wrap/full/empty task receive.
 for tick in [0,0xffffffff,0x80000000]:
  ms=pair()
  for m in ms:m.w(TICK,tick)
  for i in range(4):step('notify_full_%d'%i,ms,'notify')
  for i in range(4):step('get_empty_%d'%i,ms,'get')
  step('notify_after_wrap',ms,'notify');step('get_after_wrap',ms,'get');step('consume_queued',ms,'consume')
 # Rearm before receive: tick immutable but selected pointer can change. Synthetic
 # NEXTCTRL clear models peripheral progress; no scheduling/hardware evidence.
 for rearms,txbusy,age in itertools.product([0,1,2,3],[False,True],[0,40,41]):
  ms=pair()
  for m in ms:m.w(TICK,0xfffffff0)
  step('sequence_notify',ms,'notify')
  for i in range(rearms):
   for m in ms:m.w(0x4020821c,2 if txbusy else 0)
   step('sequence_rearm',ms,'service',[24])
  for m in ms:m.w(TICK,0xfffffff0+age)
  step('sequence_get',ms,'get');step('sequence_consume',ms,'consume',change_pcm=age<41)
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 components=['audio_pcm_consumer','audio_dma_rearm','audio_cache_handoff','cache_maintenance','freertos_queue','freertos_daemon']
 result=dict(status='PASS',calls=calls,results=results,original_trace=trace,unique_original_trace_bytes=len(used),firmware_sha256=sha(blob),elf_sha256=sha(args.elf),source_manifest={str(p.relative_to(ROOT)):sha(p) for c in components for p in (ROOT/'g2/components/foundation'/c).iterdir() if p.suffix in ['.c','.h','.py']},limits='No executable callee stubs. Stop before callback entry, DSP57ae56, logging43d0ce, wake449238. Source seams return new descriptors, not stock ABI returns. Queues coherent12B data, unlockedTX, empty send/receive waitlists, task receive timeout0; scheduler unblock/disinherit/assert declarations are unexecuted boundaries. Synthetic explicit MMIO progression and buffer/registration mutation; no field race, scheduling, ownership or physical coherence proof.')
 with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print('PASS',calls,'calls',len(used),'original trace bytes')
if __name__=='__main__':main()
