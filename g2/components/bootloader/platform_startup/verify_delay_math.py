#!/usr/bin/env python3
"""Stock/source floating delay operands; ROM delay is a recorded callback."""
import argparse,hashlib,importlib.util,json,random
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Machine:
 def __init__(self,source,segments,syms):
  self.source=source;self.syms=syms;self.events=[];self.trace={};self.cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB);self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
  for lo,size in [(0,0x1000),(0x10000,0x10000),(0x410000,0x30000),(0x20000000,0x40000),(0x40021000,0x1000),(0xe000e000,0x2000),(0x08000000,0x1000)]:self.cpu.mem_map(lo,size)
  if source:
   for s in segments:self.cpu.mem_write(s['address'],s['data'])
  else:self.cpu.mem_write(0x410000,BLOB.read_bytes())
  self.cpu.hook_add(UC_HOOK_CODE,self.code)
 def code(self,uc,pc,size,user):
  if pc==0x08000000:uc.emu_stop();return
  if pc==0x40:self.events.append(['ROM-delay-cycles',uc.reg_read(a.UC_ARM_REG_R0)]);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  assert (0x10000<=pc<0x20000) if self.source else (0x41d1c0<=pc<0x41d210),(self.source,hex(pc))
  if not self.source:self.trace[hex(pc)]=bytes(uc.mem_read(pc,size)).hex()
 def call(self,arg,mode,fpscr):
  self.cpu.mem_write(0x40021000,mode.to_bytes(4,'little'));self.cpu.mem_write(0xe000ed88,(0x00f00000).to_bytes(4,'little'));self.cpu.reg_write(a.UC_ARM_REG_FPEXC,0x40000000);self.cpu.reg_write(a.UC_ARM_REG_FPSCR,fpscr)
  self.cpu.reg_write(a.UC_ARM_REG_R0,arg);self.cpu.reg_write(a.UC_ARM_REG_R7,0x76543210);self.cpu.reg_write(a.UC_ARM_REG_SP,0x2003f000);self.cpu.reg_write(a.UC_ARM_REG_LR,0x08000001)
  self.cpu.emu_start(self.syms['opencfw_boot_delay_us_math'] if self.source else 0x41d1c1,0,count=1000);assert self.cpu.reg_read(a.UC_ARM_REG_PC)==0x08000000
  return dict(events=self.events,r0=self.cpu.reg_read(a.UC_ARM_REG_R0),r1=self.cpu.reg_read(a.UC_ARM_REG_R1),r7=self.cpu.reg_read(a.UC_ARM_REG_R7),sp=self.cpu.reg_read(a.UC_ARM_REG_SP),s0=self.cpu.reg_read(a.UC_ARM_REG_S0),s1=self.cpu.reg_read(a.UC_ARM_REG_S1),fpscr=self.cpu.reg_read(a.UC_ARM_REG_FPSCR))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert sha(BLOB)==SHA;_,segments,syms=elf.elf_info(args.elf);rng=random.Random(0x41d1c0);values=[0,1,2,10,15,24,31,32,1000,0xffffff,0x1000001,0x7ffffff,0x8000000,0x80000000,0xffffffff]+[rng.getrandbits(32) for _ in range(24)];cases=[];trace={}
 for arg in values:
  for mode in [0,8,16,24,0xffffffff]:
   for fpscr in [0x02040000,0x02440000,0x02840000,0x02c40000]:
    pair=[Machine(False,segments,syms),Machine(True,segments,syms)];r=[m.call(arg,mode,fpscr) for m in pair];assert r[0]==r[1],(arg,mode,fpscr,r);trace.update(pair[0].trace);cases.append(dict(argument=arg,mode=mode,fpscr=fpscr,result=r[0]))
 used={int(pc,16)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))};report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=SHA,elf_sha256=sha(args.elf),source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),Path(__file__).with_name('delay_math.S'),Path(__file__).with_name('delay_math.ld')]},comparisons=cases,original_trace=trace,limits=['Resident ROM Thumb41 is intercepted and its input recorded; no ROM body, elapsed-time, hardware clock or FPU exception behavior proof.','Original and reconstructed instruction math, FP rounding modes/status/register effects and arguments are compared on a compatible Cortex-M33 Unicorn model. This is not byte-identical output or physical Cortex-M55 validation.']);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
