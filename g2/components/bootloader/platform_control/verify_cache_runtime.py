#!/usr/bin/env python3
"""Stock/source cache operands, write/barrier order; no physical cache model."""
import argparse,hashlib,json,importlib.util
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('elf_reader',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Machine:
 def __init__(self,source,segments,syms):
  self.source=source;self.events=[];self.trace={};self.cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB);self.cpu.mem_map(0x410000,0x30000);self.cpu.mem_map(0x10000,0x20000);self.cpu.mem_map(0x20000000,0x40000);self.cpu.mem_map(0xe000e000,0x2000);self.cpu.mem_map(0x08000000,0x1000)
  if source:
   for address,data,size,flags in segments:self.cpu.mem_write(address,data)
   self.entry=syms['opencfw_boot_cache_maintain']
  else:self.cpu.mem_write(0x410000,BLOB.read_bytes());self.entry=0x41e349
  self.cpu.hook_add(UC_HOOK_CODE,self.code);self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=0xe000e000,end=0xe000ffff)
 def code(self,uc,pc,size,user):
  if pc==0x08000000:uc.emu_stop();return
  raw=bytes(uc.mem_read(pc,size))
  if not self.source:self.trace[hex(pc)]=raw.hex()
  if raw.hex()=='bff34f8f':self.events.append(['dsb'])
  elif raw.hex()=='bff36f8f':self.events.append(['isb'])
 def write(self,uc,access,address,size,value,user):self.events.append(['write',hex(address),size,value])
 def call(self,enabled,descriptor,range_value,operation):
  self.cpu.mem_write(0xe000ed14,(enabled<<16).to_bytes(4,'little'));self.cpu.mem_write(0xe000ed80,descriptor.to_bytes(4,'little'))
  pointer=0 if range_value is None else 0x20002000
  if pointer:self.cpu.mem_write(pointer,b''.join(x.to_bytes(4,'little') for x in range_value))
  self.cpu.reg_write(a.UC_ARM_REG_R0,pointer);self.cpu.reg_write(a.UC_ARM_REG_R1,operation);self.cpu.reg_write(a.UC_ARM_REG_SP,0x2003f000);self.cpu.reg_write(a.UC_ARM_REG_LR,0x08000001)
  self.cpu.emu_start(self.entry,0,count=200000);assert self.cpu.reg_read(a.UC_ARM_REG_PC)==0x08000000
  return self.cpu.reg_read(a.UC_ARM_REG_R0),self.events
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert sha(BLOB)==SHA
 _,segments,syms=elf.elf_info(args.elf);cases=[];trace={}
 ranges=[None,(0x438000,0),(0x438000,1),(0x438000,32),(0x438003,32),(0x43801f,33),(0xfffffff0,65),(0,0xffffffff),(0,0x80000000)]
 for enabled in [0,1]:
  for descriptor in [0,(2<<13)|(1<<3),(0x200<<13)|(3<<3)]:
   for rg in ranges:
    for op in [0,1,0x100,0x101,0xff]:
     pair=[Machine(False,segments,syms),Machine(True,segments,syms)];results=[m.call(enabled,descriptor,rg,op) for m in pair];assert results[0]==results[1],(enabled,descriptor,rg,op,results)
     trace.update(pair[0].trace);cases.append(dict(enabled=enabled,descriptor=hex(descriptor),range=rg,operation=hex(op),events=results[0][1]))
 used={int(pc,16)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=SHA,elf_sha256=sha(args.elf),source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),Path(__file__).with_name('cache_runtime.c'),Path(__file__).with_name('cache_module.ld')]},comparisons=cases,original_trace=trace,limits=['SCB cache registers are synthetic memory; original/source MMIO operands and barrier order agree. No real cache-line invalidation, memory visibility, instruction fetch coherence or hardware interrupt timing is proved.','Matrix covers disabled path, set/way combinations, range alignment, signed nonpositive lengths, count/address wrap and low-byte operation truncation. It does not measure physical cache geometry.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
