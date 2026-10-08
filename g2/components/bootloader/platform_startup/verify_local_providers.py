#!/usr/bin/env python3
"""Original/source register, MMIO and wrapper-call equivalence; no hardware."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ENTRIES={'coprocessor_enable':0x41ac44,'fp_lazy_mode':0x41ac5a,'delay_scaled':0x41f9d8,'delay_raw':0x41f9e6}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Machine:
 def __init__(self,source,segments,syms):
  self.source=source;self.syms=syms;self.events=[];self.trace={};self.cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB);self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
  for address,size in [(0x410000,0x30000),(0x10000,0x10000),(0x20000000,0x40000),(0xe000e000,0x2000),(0x08000000,0x1000)]:self.cpu.mem_map(address,size)
  if source:
   for s in segments:self.cpu.mem_write(s['address'],s['data'])
  else:self.cpu.mem_write(0x410000,BLOB.read_bytes())
  self.cpu.hook_add(UC_HOOK_CODE,self.code);self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=0xe000e000,end=0xe000ffff)
 def ret(self,value):self.cpu.reg_write(a.UC_ARM_REG_R0,value);self.cpu.reg_write(a.UC_ARM_REG_PC,self.cpu.reg_read(a.UC_ARM_REG_LR))
 def code(self,uc,pc,size,user):
  if pc==0x08000000:uc.emu_stop();return
  if pc==(0x08000100 if self.source else 0x41b8ec):
   previous=uc.reg_read(a.UC_ARM_REG_PRIMASK);self.events.append(['critical-save',previous]);uc.reg_write(a.UC_ARM_REG_PRIMASK,1);self.ret(previous);return
  if pc==(0x08000120 if self.source else 0x41d1c0):self.events.append(['delay-us-argument',uc.reg_read(a.UC_ARM_REG_R0)]);self.ret(0xabcd);return
  raw=bytes(uc.mem_read(pc,size))
  if not self.source:self.trace[hex(pc)]=raw.hex()
  if raw.hex()=='bff34f8f':self.events.append(['dsb'])
  if raw.hex()=='bff36f8f':self.events.append(['isb'])
 def write(self,uc,access,address,size,value,user):self.events.append(['write',hex(address),size,value])
 def call(self,name,arg,initial,mask):
  self.cpu.mem_write(0xe000ed88,initial.to_bytes(4,'little'));self.cpu.mem_write(0xe000ef34,initial.to_bytes(4,'little'))
  for i in range(13):self.cpu.reg_write(getattr(a,'UC_ARM_REG_R'+str(i)),0x100+i)
  self.cpu.reg_write(a.UC_ARM_REG_R0,arg);self.cpu.reg_write(a.UC_ARM_REG_SP,0x2003f000);self.cpu.reg_write(a.UC_ARM_REG_LR,0x08000001);self.cpu.reg_write(a.UC_ARM_REG_PRIMASK,mask)
  entry=self.syms['opencfw_boot_'+name] if self.source else ENTRIES[name]|1
  self.cpu.emu_start(entry,0,count=10000);assert self.cpu.reg_read(a.UC_ARM_REG_PC)==0x08000000
  return dict(events=self.events,return_registers=[self.cpu.reg_read(getattr(a,'UC_ARM_REG_R'+str(i))) for i in [0,1,4,5,6,7,8,9,10,11]],sp=self.cpu.reg_read(a.UC_ARM_REG_SP),primask=self.cpu.reg_read(a.UC_ARM_REG_PRIMASK),cpacr=self.cpu.mem_read(0xe000ed88,4).hex(),fpccr=self.cpu.mem_read(0xe000ef34,4).hex())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert sha(BLOB)==SHA;_,segments,syms=elf.elf_info(args.elf);cases=[];trace={}
 for name in ENTRIES:
  for arg in [0,1,0x100,0x101,0xffffffff,0x80000000]:
   for initial in [0,0x12345678,0xffffffff]:
    for mask in [0,1]:
     pair=[Machine(False,segments,syms),Machine(True,segments,syms)];result=[m.call(name,arg,initial,mask) for m in pair];assert result[0]==result[1],(name,arg,initial,mask,result);trace.update(pair[0].trace);cases.append(dict(function=name,argument=arg,initial=initial,primask=mask,result=result[0]))
 used={int(pc,16)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=SHA,elf_sha256=sha(args.elf),source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),Path(__file__).with_name('local_providers.S'),Path(__file__).with_name('local_providers.ld')]},comparisons=cases,original_trace=trace,limits=['Critical-save callee and HAL delay are explicit controlled callbacks. Tests establish wrapper operands, volatile stores/barriers, PRIMASK restoration and return/callee-saved register behavior; no physical delay, FPU exception timing or silicon ordering measurement.','Scaled delay uses unsigned 32-bit multiplication by1000; raw delay forwards unchanged. Low-byte FP mode truncation and preexisting control bits covered.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
