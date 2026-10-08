#!/usr/bin/env python3
"""Original/source ADC context+channel configuration leaf comparisons."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import arm_const as a
spec=importlib.util.spec_from_file_location('adc',Path(__file__).with_name('verify_adc_control.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class Machine(v.Machine):
 def memwrite(self,uc,access,address,size,value,user):
  super().memwrite(uc,access,address,size,value,user)
  if 0x4003800c<=address<=0x40038040 and not 0x4003802c<=address<=0x40038034:self.records.append([address,size,value&0xffffffff])
 def call_config(self,kind,handle,index,pointer):
  self.done=False;self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000)
  params=(handle,pointer,0) if kind=='context' else (handle,index,pointer)
  for reg,value in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2),params):self.cpu.reg_write(reg,value)
  self.cpu.reg_write(a.UC_ARM_REG_SP,v.v.v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.v.v.STOP|1)
  name='opencfw_bl_adc_context_configure' if kind=='context' else 'opencfw_bl_adc_configure_channel';pc=self.symbols[name]&~1 if self.source else 0x42eb74 if kind=='context' else 0x42eaf6
  self.cpu.emu_start(pc|1,v.v.v.STOP+2,count=1000);assert self.done;return self.cpu.reg_read(a.UC_ARM_REG_R0)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args();_,segs,syms=v.v.v.elf.elf_info(args.elf);cases=[];trace={}
 def compare(kind,handle=0x20026df0,flags=0x01afafaf,index=0,mode=7,selector=0x20,tail=(0,3,0,1),counter=0,repeat=1,pointer=v.ARGS):
  results=[]
  for source in (False,True):
   m=Machine(source,segs,syms,dict(values=[0]*5,rom_status=0));m.w(0x20026df0,flags);m.w(0x20026df4,0);m.w(0x2002702c,counter);m.cpu.mem_write(v.ARGS,bytes([mode,mode,0,0])+struct.pack('<I',selector)+bytes(tail));m.records.clear()
   status=[m.call_config(kind,handle,index,pointer) for _ in range(repeat)];results.append(dict(status=status,writes=m.records,mmio=bytes(m.cpu.mem_read(0x4003800c,0x38)).hex(),counter=m.r(0x2002702c),arguments=bytes(m.cpu.mem_read(v.ARGS,12)).hex(),reads=m.reads))
   if not source:trace.update({hex(pc):raw for pc,raw in m.trace.items()})
  assert results[0]==results[1],(kind,handle,flags,index,mode,selector,tail,results);cases.append(dict(kind=kind,fixture=dict(handle=hex(handle),flags=hex(flags),index=index,mode=mode,selector=selector,tail=tail,counter=counter,repeat=repeat,pointer=hex(pointer)),observation=results[0]));return results[0]
 for kind,handle,flags in itertools.product(('context','channel'),(0,0x20026df0),(0,0x01afafaf,0x03afafaf,0xffafafaf)):
  o=compare(kind,handle=handle,flags=flags);assert o['status']==[0 if handle and flags&0x01ffffff==0x01afafaf else 2]
 for mode,threshold in itertools.product((0,1,7,8,255),(0,1,0x3ff,0x400,0xffffffff)):
  o=compare('context',mode=mode,selector=threshold);assert o['writes']==[[0x40038040,4,((mode&7)<<16)|(threshold&0x3ff)]] and o['counter']==0
 for index,selector in itertools.product((0,7,8,256,0xffffffff),(0,0x1f,0x20,0x3f,0x40,0xffffffff)):
  o=compare('channel',index=index,selector=selector);assert o['status']==[5 if index>=8 else 6 if selector<0x20 or selector>=0x40 else 0]
 for mode,tail in itertools.product((0,7,8,255),((0,0,0,0),(3,15,1,1),(255,255,255,255),(4,16,2,2))):
  o=compare('channel',mode=mode,tail=tail);expected=((mode&7)<<24)|(0x20<<18)|((tail[0]&3)<<16)|((tail[1]&15)<<8)|(tail[2]<<1)|tail[3];assert o['writes']==[[0x4003800c,4,expected],[0x2002702c,4,1]]
 for count in (0,7,0xfffffffe,0xffffffff):
  o=compare('channel',counter=count,repeat=2);assert o['counter']==(count+2)&0xffffffff
 compare('context',pointer=0);assert compare('channel',pointer=0)['status']==[6]
 blob=v.v.v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==v.v.v.LOCKED_SHA
 for pc,raw in trace.items():p=int(pc,16);assert blob[p-v.v.v.BASE:p-v.v.v.BASE+len(bytes.fromhex(raw))]==bytes.fromhex(raw)
 ranges=[(0x42eaf6,0x42eb74),(0x42eb74,0x42ebaa)];visited=sum(len(bytes.fromhex(raw)) for pc,raw in trace.items() if any(lo<=int(pc,16)<hi for lo,hi in ranges));assert visited==180
 r=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.v.v.LOCKED_SHA,original_trace=trace,visited_body_bytes=visited,comparisons=cases,limits=['Direct function-only execution of the supplied compiled ELF; shared-image startup comparisons, when present, are separate receipts.','Original/source instructions execute without external-call stubs; MMIO and calibration counter are mapped RAM.','NULL preliminary context read/argument fields at0 are mapped ROM in harness; fault behavior on hardware not certified.','Repeated configuration increments global counter without allocation, saturation or locking. No physical channel programming or concurrency proof.']);args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256','visited_body_bytes']}))
if __name__=='__main__':main()
