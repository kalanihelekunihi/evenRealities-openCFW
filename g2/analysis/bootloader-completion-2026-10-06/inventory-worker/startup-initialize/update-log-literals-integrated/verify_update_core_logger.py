#!/usr/bin/env python3
"""Bounded original/source execution. Filesystem/log/flash callbacks are synthetic.
Direct CRC, mode, memcmp and architectural handoff use no returning provider stub.
"""
import argparse, hashlib, importlib.util, json, random, struct, zlib
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a
ROOT=Path.cwd()
spec=importlib.util.spec_from_file_location('elf_reader',ROOT/'g2/components/bootloader/update_core/elf_reader.py')
elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
BASE=0x410000;STOP=0x08000000;SP=0x2002f000
HANDLE=0x20001000;HEADER=0x20002000;DESC=0x20003000;SEED=0x20004000;DATA=0x20005000
FLASH=0x90000000;ERASE=0x08002000;READ=0x08002010;PROGRAM=0x08002020;RESET=0x08002030
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ENTRIES={'crc32':0x42e1ec,'stream_mode':0x42d84c,'memcmp':0x415758,'erase_visit':0x42d9f0,'compare':0x42da1e,'verify':0x42d890,'program':0x42dae8,'vector_handoff':0x42dc90}
PROVIDERS={0x4153a4:'open',0x4154d2:'prepare',0x415484:'read',0x415446:'close',0x4176ce:'log',0x41e348:'runtime',ERASE:'erase',READ:'flash_read',PROGRAM:'program'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Machine:
 def __init__(self,source=False,segments=(),symbols=None):
  self.source=source;self.symbols=symbols or {};self.cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);self.events=[];self.trace={};self.file=b'';self.position=0;self.open_value=0x51;self.short=None;self.read_calls=0;self.corrupt=None;self.finished=False
  self.cpu.mem_map(BASE,0x25000)
  if not source:self.cpu.mem_write(BASE,BLOB.read_bytes())
  self.cpu.mem_map(0x20000000,0x40000);self.cpu.mem_map(STOP,0x10000);self.cpu.mem_map(0xe000e000,0x2000);self.cpu.mem_map(FLASH,0x20000)
  self.exec_ranges=[]
  if source:
   for s in segments:
    lo=s['address']&~4095;hi=(s['address']+s['memory_size']+4095)&~4095
    # PT_LOAD SRAM/BSS may already be covered by the common SRAM mapping.
    # Allocate only uncovered segments and initialize the full memory extent.
    if not any(a<=lo and hi-1<=b for a,b,_ in self.cpu.mem_regions()):self.cpu.mem_map(lo,hi-lo)
    if s['data']:self.cpu.mem_write(s['address'],s['data'])
    tail=s['memory_size']-len(s['data'])
    if tail:self.cpu.mem_write(s['address']+len(s['data']),b'\0'*tail)
    if s['flags']&1:self.exec_ranges.append((s['address'],s['address']+len(s['data'])))
  else:self.exec_ranges=[(BASE,BASE+BLOB.stat().st_size)]
  self.w(0x200004f0,DESC);self.w(DESC+4,4096);self.w(DESC+0x18,READ|1);self.w(DESC+0x1c,PROGRAM|1);self.w(DESC+0x20,ERASE|1)
  self.cpu.mem_write(0x2001ede0,b'\xa5'*8200);self.cpu.mem_write(0x2001fdf0,b'\xa5'*4096)
  self.cpu.hook_add(UC_HOOK_CODE,self.code)
 def w(self,p,x):self.cpu.mem_write(p,struct.pack('<I',x&0xffffffff))
 def u(self,p):return struct.unpack('<I',self.cpu.mem_read(p,4))[0]
 def args(self):return [self.cpu.reg_read(r) for r in [a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3]]
 def ret(self,value=0):self.cpu.reg_write(a.UC_ARM_REG_R0,value&0xffffffff);self.cpu.reg_write(a.UC_ARM_REG_PC,self.cpu.reg_read(a.UC_ARM_REG_LR))
 def code(self,uc,pc,size,_):
  if pc==STOP:self.finished=True;uc.emu_stop();return
  if pc==RESET:
   self.finished=True;self.events.append(['handoff',self.u(0xe000ed08),uc.reg_read(a.UC_ARM_REG_SP),pc]);uc.emu_stop();return
  if self.source:
   aliases={'opencfw_boot_file_open':0x4153a4,'opencfw_boot_file_prepare':0x4154d2,'opencfw_boot_file_read':0x415484,'opencfw_boot_file_close':0x415446,'opencfw_boot_elog_output':0x4176ce,'opencfw_boot_runtime_call':0x41e348}
   pc={self.symbols[k]&~1:v for k,v in aliases.items() if k in self.symbols}.get(pc,pc)
  if pc in PROVIDERS:
   kind=PROVIDERS[pc];r0,r1,r2,r3=self.args()
   if kind=='open':self.events.append([kind,r0,r1]);self.position=0;self.ret(self.open_value)
   elif kind=='prepare':self.events.append([kind,r0,r1,r2]);self.position=r1;self.ret()
   elif kind=='read':
    n=r1*r2;got=min(n,max(0,len(self.file)-self.position))
    short=self.short.get(self.read_calls) if isinstance(self.short,dict) else (self.short if self.read_calls==0 else None)
    if short is not None:got=min(got,short)
    self.read_calls+=1;self.cpu.mem_write(r0,self.file[self.position:self.position+got]);self.position+=got;self.events.append([kind,r0,r1,r2,r3,got]);self.ret(got)
   elif kind=='close':self.events.append([kind,r0]);self.ret()
   elif kind=='log':
    import re
    def string(p):
     raw=bytearray()
     while self.cpu.mem_read(p,1)[0]:raw+=self.cpu.mem_read(p,1);p+=1
     return raw.decode('utf-8',errors='backslashreplace')
    sp=uc.reg_read(a.UC_ARM_REG_SP);w=list(struct.unpack('<8I',self.cpu.mem_read(sp,32)));fmt=string(w[1]);arguments=[string(v) if kind=='s' else v for kind,v in zip(re.findall(r'%(?:z)?([sdux])',fmt),w[2:])];self.events.append(['full-log',r0,string(r1),string(r2),string(r3),w[0],fmt,arguments]);self.ret()
   elif kind=='runtime':self.events.append([kind,r0,r1]);self.ret()
   elif kind=='erase':self.events.append([kind,r0]);self.cpu.mem_write(r0,b'\xff'*4096);self.ret()
   elif kind=='flash_read':self.events.append([kind,r0,r1,r2]);self.cpu.mem_write(r0,bytes(self.cpu.mem_read(r1,r2)));self.ret()
   elif kind=='program':
    self.events.append([kind,r0,r1,r2]);self.cpu.mem_write(r0,bytes(self.cpu.mem_read(r1,r2)))
    if self.corrupt is not None:self.cpu.mem_write(r0+self.corrupt,b'\xee')
    self.ret()
   return
  assert any(lo<=pc<hi for lo,hi in self.exec_ranges),(self.source,hex(pc),'unimplemented execution')
  if not self.source:self.trace[hex(pc)]=bytes(uc.mem_read(pc,size)).hex()
 def run(self,name,args):
  self.finished=False;self.events=[];entry=(self.symbols['opencfw_boot_'+name]&~1) if self.source else ENTRIES[name]
  for reg,value in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3],args+[0]*4):self.cpu.reg_write(reg,value)
  self.cpu.reg_write(a.UC_ARM_REG_SP,SP);self.cpu.reg_write(a.UC_ARM_REG_LR,STOP|1);self.cpu.emu_start(entry|1,STOP+2,count=2000000);assert self.finished,(name,'execution budget')
  return {'return':self.cpu.reg_read(a.UC_ARM_REG_R0),'events':self.events,'handle':self.u(HANDLE),'crc_buffer_sha':hashlib.sha256(self.cpu.mem_read(0x2001fdf0,4096)).hexdigest(),'program_buffer_sha':hashlib.sha256(self.cpu.mem_read(0x2001ede0,4096)).hexdigest(),'flash_sha':hashlib.sha256(self.cpu.mem_read(FLASH,0x20000)).hexdigest()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert sha(BLOB)==SHA;_,segments,symbols=elf.elf_info(args.elf);trace={};cases=[]
 def pair():return [Machine(),Machine(True,segments,symbols)]
 def check(name,ms,params,extra=None):
  try: results=[m.run(name,params) for m in ms]
  except Exception:
   print('failure',name,params,[(m.source,hex(m.cpu.reg_read(a.UC_ARM_REG_PC))) for m in ms]);raise
  if name in ['erase_visit','program','vector_handoff']:results=[{k:v for k,v in r.items() if k!='return'} for r in results]
  assert results[0]==results[1],(name,params,{k:[r[k] for r in results] for k in results[0] if results[0][k]!=results[1][k]})
  trace.update(ms[0].trace);cases.append(dict(function=name,arguments=params,fixture=extra,original=results[0],source=results[1]))
 rng=random.Random(20261006)
 for size in [0,1,4095,4096,4097,8192]:
  for mismatch in [None,0,4096]:
   if mismatch is not None and mismatch>=size:continue
   ms=pair();data=rng.randbytes(size)
   for m in ms:
    if size:m.cpu.mem_write(DATA,data);m.cpu.mem_write(FLASH,data)
    if mismatch is not None:m.cpu.mem_write(FLASH+mismatch,b'\xee' if data[mismatch]!=0xee else b'\xef')
   check('compare',ms,[FLASH,DATA,size,DESC],{'mismatch':mismatch})
 for size in [0,1,31,4095,4096,4097,8192]:
  for opened,short,correct in [(True,None,True),(True,None,False),(True,0,False),(True,3,False),(True,{1:7},False),(False,None,False)]:
   ms=pair();data=rng.randbytes(size);expected=zlib.crc32(data)+(0 if correct else 1)
   for m in ms:
    m.file=b'header08'+data;m.open_value=0x51 if opened else 0;m.short=short;m.w(HEADER,size+8);m.w(HEADER+4,expected);m.w(0x20026efc,expected)
   check('verify',ms,[HANDLE,HEADER],{'size':size,'opened':opened,'short':short,'crc_matches':correct})
 for size in [0,1,31,4095,4096,4097,8192]:
  for opened,short,corrupt in [(True,None,None),(True,0,None),(True,None,0),(True,3,None),(True,{1:7},None),(False,None,None)]:
   ms=pair();data=rng.randbytes(size)
   for m in ms:
    m.file=b'\0'*32+data;m.open_value=0x51 if opened else 0;m.short=short;m.corrupt=corrupt;m.w(HEADER,size+32);m.w(HEADER+20,FLASH)
   check('program',ms,[HANDLE,HEADER],{'size':size,'opened':opened,'short':short,'corrupt':corrupt})
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 result={'status':'PASS','cases':len(cases),'per_function':{name:sum(c['function']==name for c in cases) for name in ENTRIES},'original_sha256':SHA,'elf_sha256':sha(args.elf),'source_sha256':{p.name:sha(p) for p in Path(__file__).parent.iterdir() if p.suffix in ['.c','.h','.S','.ld','.py']},'original_trace':trace,'distinct_original_trace_bytes':len(used),'comparisons':cases,'limits':['Filesystem/log/runtime/storage providers above are synthetic intercepted fixtures, not source-defined implementations.','Only compare/verify/program families tested here; inlined/direct CRC/memcmp routines execute inside them. Existing independent leaf regressions remain separate.','Full log metadata and only format-consumed arguments compare. Final ---Install end--- format has no placeholders; incidental R13/R8 values are not consumed. Actual update core instructions and fixed readonly strings execute/load; lower filesystem/runtime/flash/logger-output remain declared controlled providers.','No physical erase/program, interruption, cache/flash coherence, task scheduling, vector validation or end-to-end boot demonstrated.','Size underflow, zero chunk, malicious pointers and dynamic provider mutation not accepted as tested-safe inputs.','Source ELF references explicit unresolved platform provider symbols; it is a callable test module, not a bootable payload.']}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','cases','per_function','distinct_original_trace_bytes']},indent=2))
if __name__=='__main__':main()
