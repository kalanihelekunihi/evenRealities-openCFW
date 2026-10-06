#!/usr/bin/env python3
"""Registration lifecycle and code-derived observation audit; no provider stubs."""
import argparse,importlib.util,json,struct,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('v',ROOT/'g2/components/foundation/audio_pcm_consumer/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
FLAGS=0x20004543;OUT=v.CUT+256
class Machine(v.Machine):
 def __init__(self,segments,symbols=None,profile='none'):
  self.registration=False;self.stores=[];self.profile=profile;self.decoded={}
  super().__init__(segments,symbols)
  if profile=='none':
   # Installed Unicorn2.1.4 callback handles: constructor adds code then5 MEM.
   handles=list(self.cpu._callbacks);assert len(handles)==6
   for handle in handles[1:]:self.cpu.hook_del(handle)
  from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
  self.md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);self.md.detail=True
 def reg(self,uc,i,reg):
  name=i.reg_name(reg);name={'ip':'r12','sb':'r9','sl':'r10','fp':'r11'}.get(name,name)
  return uc.reg_read(getattr(self.a,'UC_ARM_REG_'+name.upper()))
 def observe(self,uc,pc,size):
  from capstone.arm import ARM_OP_MEM
  if pc not in self.decoded:self.decoded[pc]=next(self.md.disasm(bytes(uc.mem_read(pc,size)),pc))
  i=self.decoded[pc];writes=[]
  if i.mnemonic.startswith('str') and len(i.operands)>=2 and i.operands[1].type==ARM_OP_MEM:
   m=i.operands[1].mem;at=(self.reg(uc,i,m.base)+m.disp+(self.reg(uc,i,m.index) if m.index else 0))&0xffffffff
   width=1 if i.mnemonic.startswith('strb') else 2 if i.mnemonic.startswith('strh') else 4
   assert not i.mnemonic.startswith('strd');writes=[(at,width,self.reg(uc,i,i.operands[0].reg))]
  elif i.mnemonic.startswith('stm'):
   regs=[op.reg for op in i.operands[1:]];at=self.reg(uc,i,i.operands[0].reg)-(4*len(regs) if i.mnemonic.startswith('stmdb') else 0)
   writes=[(at+4*n,4,self.reg(uc,i,reg)) for n,reg in enumerate(regs)]
  for at,width,value in writes:
   relevant=(v.TABLE<=at<v.TABLE+48 or v.H<=at<v.H+128 or v.Q<=at<v.Q+80 or v.DATA<=at<v.DATA+36 or at in [v.COUNT,0x2000309c] or 0x40208000<=at<0x40208400 or 0xe000e000<=at<0xe0010000)
   if relevant:
    # Byte normalization retains order without equating source byte stores to
    # architecture-level multiword atomicity or real device transactions.
    for n in range(width):self.stores.append([hex(at+n),(value>>(8*n))&255])
  if i.mnemonic in ['dsb','isb']:self.stores.append([i.mnemonic])
 def code(self,uc,pc,size,_):
  if self.registration:
   if pc==v.cache.STOP:uc.emu_stop();return
   if not self.source and pc in [0x43d574,0x43ce9e]:self.cut=dict(provider=pc);uc.emu_stop();return
   s=next((s for s in self.segments if s['flags']&1 and s['address']<=pc< s['address']+len(s['data'])),None);assert s,hex(pc)
   raw=bytes(uc.mem_read(pc,size));assert raw==s['data'][pc-s['address']:pc-s['address']+size];self.trace[hex(pc)]=raw.hex()
  else:
   super().code(uc,pc,size,_)
   if pc==v.cache.STOP or self.cut is not None:return
  self.observe(uc,pc,size)
 def snapshot(self):
  # Compare all mapped RAM except independent source observation outputs and
  # live local-stack area; no observer callbacks are required for this check.
  b=bytearray(self.cpu.mem_read(0x20000000,0x80000));b[0xe000:0xf000]=b'\0'*4096;b[v.CUT-0x20000000:v.CUT-0x20000000+24]=b'\0'*24;b[OUT-0x20000000:OUT-0x20000000+12]=b'\0'*12
  import hashlib
  return dict(ram_sha256=hashlib.sha256(b).hexdigest(),i2s=bytes(self.cpu.mem_read(0x40208000,1024)).hex(),scb=bytes(self.cpu.mem_read(0xe000e000,8192)).hex(),basepri=self.cpu.reg_read(self.a.UC_ARM_REG_BASEPRI),primask=self.cpu.reg_read(self.a.UC_ARM_REG_PRIMASK))
 def register(self,kind,owner,mode,callback=0):
  self.registration=True;self.cut=None;self.stores=[];self.events=[];self.callback_reads=0;self.change_callback=False;self.change_pcm=False;self.pcm_reads=0
  self.cpu.mem_write(OUT,b'\0'*12)
  entry=self.symbols['opencfw_pcm_'+kind+'_prefix']&~1 if self.source else 0x57ab78 if kind=='register' else 0x57acd0
  args=[owner,mode,callback,OUT]
  if kind=='unregister':args=[owner,mode,OUT,0]
  for reg,value in zip([self.a.UC_ARM_REG_R0,self.a.UC_ARM_REG_R1,self.a.UC_ARM_REG_R2,self.a.UC_ARM_REG_R3],args):self.cpu.reg_write(reg,value)
  self.cpu.reg_write(self.a.UC_ARM_REG_SP,v.cache.SP);self.cpu.reg_write(self.a.UC_ARM_REG_LR,v.cache.STOP|1)
  self.cpu.emu_start(entry|1,v.cache.STOP,count=10000)
  if self.source:
   provider,stage,status=struct.unpack('<IIi',self.cpu.mem_read(OUT,12));cut=dict(provider=provider)
   if not provider:cut['status']=status
  else:
   cut=self.cut or dict(provider=0,status=self.cpu.reg_read(self.a.UC_ARM_REG_R0) if self.cpu.reg_read(self.a.UC_ARM_REG_R0)<0x80000000 else self.cpu.reg_read(self.a.UC_ARM_REG_R0)-0x100000000)
  if not cut['provider']:assert self.cpu.reg_read(self.a.UC_ARM_REG_SP)==v.cache.SP
  self.registration=False
  return dict(cut=cut,stores=self.stores,snapshot=self.snapshot(),rows=bytes(self.cpu.mem_read(v.TABLE,48)).hex())
 def invoke(self,*args,**kw):
  self.stores=[];result=super().invoke(*args,**kw);result['stores']=self.stores;result['snapshot']=self.snapshot();return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 blob=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert v.sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';b=blob.read_bytes()[32:];stock=[dict(address=v.cache.BASE,memory_size=len(b),data=b,flags=5)];_,seg,sym=v.cache.elf_reader.elf_info(args.elf)
 results=[];trace={};audit=[]
 def pair(profile='none'):return Machine(stock,profile=profile),Machine(seg,sym,profile)
 def regstep(name,ms,kind,owner,mode,callback=0):
  o,s=[m.register(kind,owner,mode,callback) for m in ms];assert o==s,(name,{k:[o[k],s[k]] for k in o if o[k]!=s[k]});trace.update(ms[0].trace);results.append(dict(name=name,operation=kind,inputs=[owner,mode,callback],original=o,source=s));return o
 def step(name,ms,kind,params=()):
  o,s=[m.invoke(kind,params) for m in ms];v.compare(o,s);assert o['stores']==s['stores'],(name,'store order',o['stores'],s['stores']);assert o['snapshot']==s['snapshot'];trace.update(ms[0].trace);results.append(dict(name=name,operation=kind,original=o,source=s));return o
 for mode,callback,occupied in itertools.product([0,1,2,256,257],[0,v.CALL],[False,True]):
  ms=pair()
  for m in ms:
   m.w(v.TABLE+8,v.CALL2 if occupied else 0);m.w(v.TABLE+20,v.CALL2 if occupied else 0)
   m.cpu.mem_write(v.TABLE+5,b'\xa6\xb7\xc8');m.cpu.mem_write(v.TABLE+17,b'\xa6\xb7\xc8')
  regstep('register',ms,'register',0x10b,mode,callback)
 for mode,occupied,match in itertools.product([0,1,2,256],[False,True],[False,True]):
  ms=pair();row=v.TABLE+12*(mode&255)
  for m in ms:m.w(row,0x10b);m.w(row+8,v.CALL if occupied else 0)
  regstep('unregister_no_range_guard',ms,'unregister',0x10b if match else 9,mode)
 # Enabled logger cases stop at real logging entry, including after publication.
 for flags,occupied in itertools.product([1,2,4],[False,True]):
  ms=pair()
  for m in ms:m.cpu.mem_write(FLAGS,bytes([flags]));m.w(v.TABLE+8,v.CALL if occupied else 0)
  regstep('logger_boundary',ms,'register',7,0,v.CALL2)
 # Lifecycle integration: queued ticks survive owner changes, actual receive,
 # callback replacement, age40/41 rollover and full queue failure.
 for age in [0,40,41]:
  ms=pair()
  for m in ms:m.w(v.TICK,0xfffffff0)
  regstep('owner_A',ms,'register',7,0,v.CALL)
  for n in range(4):step('enqueue_%d'%n,ms,'notify')
  regstep('replace_B',ms,'register',8,0,v.CALL2)
  regstep('wrong_owner_cannot_clear',ms,'unregister',7,0)
  for n in range(4):step('dequeue_%d'%n,ms,'get')
  for m in ms:m.w(v.TICK,0xfffffff0+age)
  o=step('consume_new_registration',ms,'consume')
  assert o['cut']['disposition']==(1 if age<41 else 3)
  if age<41:assert o['cut']['callback']==v.CALL2
  regstep('clear_owner_B',ms,'unregister',8,0)
  if age<41:assert step('fallback_after_clear',ms,'consume')['cut']['disposition']==2
 # Observer audit: no MEM callbacks versus the scoped prior profile. Exercise
 # queue reject/wrap, DMA partialbusy and cache publication; compare code-derived
 # MMIO/RAM store order AND every nonstack/non-observation RAM byte after calls.
 for profile in ['none','scoped']:
  ms=pair(profile)
  for m in ms:m.w(v.TICK,7)
  records=[]
  for n in range(4):records.append(step('audit_'+profile,ms,'notify'))
  for n in range(4):records.append(step('audit_'+profile,ms,'get'))
  for m in ms:m.w(0x4020821c,2)
  records.append(step('audit_'+profile,ms,'service',[24]))
  for m in ms:m.w(v.MSG+8,7)
  records.append(step('audit_'+profile,ms,'consume'))
  audit.append([dict(cut=x['cut'],stores=x['stores'],snapshot=x['snapshot']) for x in records])
 assert audit[0]==audit[1]
 used={int(pc,0)+n for pc,raw in trace.items() for n in range(len(bytes.fromhex(raw)))}
 components=['audio_pcm_registration','audio_pcm_consumer','audio_dma_rearm','audio_cache_handoff','cache_maintenance','freertos_queue','freertos_daemon']
 result=dict(status='PASS',calls=len(results),results=results,original_trace=trace,unique_original_trace_bytes=len(used),observer_audit=dict(no_memory_hook_vs_scoped='PASS',calls_per_profile=10,full_RAM_except_stack_and_observation_outputs=True,code_derived_MMIO_RAM_writes=True),firmware_sha256=v.sha(blob),elf_sha256=v.sha(args.elf),source_manifest={str(p.relative_to(ROOT)):v.sha(p) for c in components for p in (ROOT/'g2/components/foundation'/c).iterdir() if p.suffix in ['.c','.h','.py']},limits='Real registration/unregistration and logging-flags getter/memset execute original instructions, no executable stubs. Logger enabled paths cut before43d574/43ce9e. Source prefixes use new observation ABI. No actual thread wake/callback/DSP execution, or concurrent ownership safety. Registered target provenance is static production diagnostic caller evidence, not proof of normal BLE route. Audit derives store bytes before executed instructions; this is not physical multiword atomicity/cache/MMIO proof.')
 with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print('PASS',len(results),'calls',len(used),'trace bytes; observer audit PASS')
if __name__=='__main__':main()
