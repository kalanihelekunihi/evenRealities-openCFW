#!/usr/bin/env python3
"""Execute locked ADC control and compiled C; FP32 instructions are not stubbed."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import arm_const as a
from unicorn import UC_HOOK_MEM_READ
spec=importlib.util.spec_from_file_location('adc',Path(__file__).with_name('verify_adc_context.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ARGS=0x20004100;TCACHE=0x20027028
class Machine(v.Machine):
 def __init__(self,source,segs,syms,fixture):
  super().__init__(source,segs,syms,fixture);self.cpu.mem_map(0x40038000,0x1000);self.cpu.reg_write(a.UC_ARM_REG_FPEXC,0x40000000);self.reads=[];self.cpu.hook_add(UC_HOOK_MEM_READ,self.read)
 def read(self,uc,access,address,size,value,user):
  if address==4 or v.TRIMS<=address<v.TRIMS+16 or v.PAIR<=address<v.PAIR+8 or address==0x20027199:self.reads.append([address,size])
 def memwrite(self,uc,access,address,size,value,user):
  super().memwrite(uc,access,address,size,value,user)
  if ARGS<=address<ARGS+16 or address==TCACHE or 0x4003802c<=address<=0x40038034:self.records.append([address,size,value&((1<<(size*8))-1)])
 def control(self,handle,request,pointer):
  self.done=False;self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000)
  for reg,val in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2),(handle,request,pointer)):self.cpu.reg_write(reg,val)
  self.cpu.reg_write(a.UC_ARM_REG_SP,v.v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.v.STOP|1);entry=self.symbols['opencfw_bl_adc_configure']&~1 if self.source else 0x42ec0c
  self.cpu.emu_start(entry|1,v.v.STOP+2,count=20000);assert self.done;return self.cpu.reg_read(a.UC_ARM_REG_R0)
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();_,segs,syms=v.v.elf.elf_info(args.elf);cases=[];trace={}
 def compare(label,request,words=None,handle=v.POOL,pointer=ARGS,flags=0x01afafaf,cache=0,trims=(0x4395c000,0x3f800000,0),marker=1,pairvalid=1,fpscr=0,sequence=False):
  words=words if words is not None else [bits(1),0xcccccccc,0xc2f6e979,0xc2f6e979];results=[]
  for source in (False,True):
   m=Machine(source,segs,syms,dict(values=list(trims)+[bits(1),bits(2)],rom_status=0,cached=True));m.w(v.POOL,flags);m.w(v.POOL+4,0);m.w(TCACHE,cache);m.w(v.CACHE,0x1f01600d)
   for p,n in zip((v.CACHE+0x38,v.CACHE+0x3c,v.CACHE+0x40,v.CACHE+0x48,v.CACHE+0x4c),list(trims)+[0,0]):m.w(p,n)
   for p,n in zip((v.TRIMS,v.TRIMS+4,v.TRIMS+8),trims):m.w(p,n)
   m.cpu.mem_write(v.TRIMS+12,bytes([marker])+b'\x99'*3);m.w(v.PAIR,0x11223344);m.w(v.PAIR+4,0x55667788);m.cpu.mem_write(0x20027199,bytes([pairvalid]));m.cpu.mem_write(ARGS,struct.pack('<4I',*words));m.cpu.reg_write(a.UC_ARM_REG_FPSCR,fpscr);m.records.clear()
   status=[]
   if sequence:
    m.w(v.POOL,0);status.append(m.call('init',[0,v.OUT]));status.append(m.call('reset',[v.POOL]));status.append(m.call('init',[0,v.OUT]))
   status.append(m.control(handle,request,pointer));o=dict(status=status,arguments=bytes(m.cpu.mem_read(ARGS,16)).hex(),cache=m.r(TCACHE),pair=bytes(m.cpu.mem_read(v.PAIR,8)).hex(),pair_valid=m.cpu.mem_read(0x20027199,1)[0],writes=m.records,fpscr=m.cpu.reg_read(a.UC_ARM_REG_FPSCR),reads=m.reads,mmio=bytes(m.cpu.mem_read(0x4003802c,12)).hex());results.append(o)
   if not source:trace.update({hex(pc):raw for pc,raw in m.trace.items()})
  assert results[0]==results[1],(label,results);cases.append(dict(label=label,observation=results[0]));return results[0]
 for req,handle,flags in itertools.product((0,1,2,3,4,255,0x102),(0,v.POOL),(0,0x01afafaf,0xffafafaf)):
  o=compare('guard-'+str((req,handle,flags)),req,handle=handle,flags=flags)
  if not handle or flags&0x01ffffff!=0x01afafaf:assert o['status']==[2]
 for upper,lower,enable in itertools.product((0,0xfffff,0x100000,0xffffffff),(0,0xfffff,0x100000),(0,1,2,255)):
  o=compare('window-'+str((upper,lower,enable)),0,[enable,upper,lower,0]);assert o['status']==[5 if upper>=0x100000 or lower>=0x100000 else 0]
 for req,sentinel,fpscr in itertools.product((1,2,3),(0xc2f6e979,0,0x80000000,0x7fc00000,0x7f800001),(0,0x1000000)):
  w=[bits(1),0xcccccccc,0xc2f6e979,0xc2f6e979];w[2 if req==1 else 3]=sentinel;o=compare('sentinel-'+str((req,sentinel,fpscr)),req,w,fpscr=fpscr);assert o['status']==[0 if sentinel==0xc2f6e979 else 7]
 for req in (1,2,3):assert compare('null-arguments-'+str(req),req,pointer=0)['status']==[6]
 for marker in (0,1,255):
  o=compare('raw-temperature-marker-'+str(marker),2,marker=marker);assert o['arguments'][24:]==struct.pack('<I',marker).hex()
 for valid in (0,1):
  o=compare('correction-valid-ignored-'+str(valid),3,pairvalid=valid);assert o['arguments']==struct.pack('<4I',0x11223344,0x55667788,0,0).hex();assert not any(p==0x20027199 for p,s in o['reads'])
 for cache,inputbits,fpscr in itertools.product((0,0x80000000,bits(50),0x7fc00000),(0,bits(1),bits(-1),1,0x7f800000,0x7fc00000),(0,0x400000,0x800000,0xc00000,0x1000000,0x2000000)):
  compare('temperature-'+str((cache,inputbits,fpscr)),1,[inputbits,0xcccccccc,0xc2f6e979,0xc2f6e979],cache=cache,fpscr=fpscr)
 for trims in ((0,0,0),(0x7fc00000,bits(1),0),(bits(299.5),bits(1),0),(bits(299.5),1,0)):
  compare('temperature-trims-'+str(trims),1,trims=trims)
 o=compare('finite-cold-reference',1,trims=(bits(299.5),bits(1),0));assert o['cache']==bits(9.5)
 o=compare('warm-init-reset-does-not-invalidate',1,cache=bits(50),sequence=True);assert o['cache']==bits(50)
 compare('invalid-calibration-stale-correction-getter',3,sequence=True)
 blob=v.v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==v.v.LOCKED_SHA
 for pc,raw in trace.items():p=int(pc,16);assert blob[p-v.v.BASE:p-v.v.BASE+len(bytes.fromhex(raw))]==bytes.fromhex(raw)
 visited=sum(len(bytes.fromhex(raw)) for pc,raw in trace.items() if 0x42ec0c<=int(pc,16)<0x42ed60)
 report=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.v.LOCKED_SHA,original_trace=trace,control_visited_bytes=visited,comparisons=cases,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits=['Control FP32 original/source instructions execute without FP stubs; FPSCR rounding, DN and FZ fixture combinations compared. Peripheral MMIO modeled as RAM.','Combined initialization uses explicit residentROM48 word fixture only when requested; no actual OTP/factory calibration.','NULL handle preliminary load at address4 is mapped ROM RAM in the harness; actual invalid memory behavior not certified.','Source preserves stale calibration getter/cache behavior; no physical analog, IRQ, scheduling or all-input proof.']);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','cases','elf_sha256','control_visited_bytes')}))
if __name__=='__main__':main()
