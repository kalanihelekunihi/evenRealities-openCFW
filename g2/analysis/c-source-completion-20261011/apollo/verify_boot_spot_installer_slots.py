#!/usr/bin/env python3
"""Bounded stock/source SPOT installer slot and variant-state comparison."""
from pathlib import Path
import hashlib, importlib.util, json, struct
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ELF=ROOT/'g2/analysis/c-source-completion-20261011/apollo/boot-coplacement-hf2-store-order-round/boot.elf'
_,segments,symbols=v.elf.elf_info(ELF, source_coplacement=True)
class Machine(v.Machine):
 def __init__(self,source=False):
  super().__init__(False)
  if source:
   self.source=True;self.symbols=symbols;self.cpu.mem_map(0x435000,0xb000)
   self.exec_ranges=[]
   for segment in segments:
    start=segment["address"];end=start+segment["memory_size"]
    if segment["data"]:self.cpu.mem_write(start,segment["data"])
    if end>start+len(segment["data"]):self.cpu.mem_write(start+len(segment["data"]),bytes(end-start-len(segment["data"])))
    if segment["flags"]&1:self.exec_ranges.append((start,start+len(segment["data"])))
  self.cpu.mem_map(0x40020000,0x3000)
  self.cpu.mem_write(0x20026e38,b'\xa5'*60)
 def code(self,uc,pc,size,user):
  callback=self.u(0x20026e38)&~1
  if callback and callback!=0xa5a5a5a4 and pc==callback:
   self.events.append(['slot0-call',callback]);self.ret(0);return
  super().code(uc,pc,size,user)
 def invoke(self,rev,var):
  self.w(0x4002000c,rev);self.w(0x20000098,var);self.w(0x2002682c,0)
  entry=(self.symbols['opencfw_boot_startup_spot_dispatch']&~1) if self.source else 0x41ce52
  for r in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3):self.cpu.reg_write(r,0)
  self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1)
  try:self.cpu.emu_start(entry|1,v.STOP+2,count=500000)
  except Exception:
   print("source" if self.source else "stock",rev,var,hex(self.cpu.reg_read(a.UC_ARM_REG_PC)));raise
  raw=bytes(self.cpu.mem_read(0x20026e38,60))
  offsets=[i for i in range(0,60,4) if struct.unpack_from('<I',raw,i)[0]!=0]
  flags=bytes(self.cpu.mem_read(0x200271a9,6)).hex()
  return {'offsets':offsets,'flags':flags,'result':self.cpu.reg_read(a.UC_ARM_REG_R0)}
results=[]
for rev in (33,34,35,36):
 for var in (0,1,2,3):
  n=Machine();result=n.invoke(rev,var)
  results.append({'rev':rev,'var':var,'stock':result})
out=Path(__file__).with_name('boot-spot-installer-stock-matrix.json')
report={'status':'PASS_BOUNDED_STOCK_SLOT_MATRIX','cases':len(results),'stock_sha256':v.SHA,'results':results,'limits':['Executes authenticated stock installer with slot-zero callback cut to return zero; records nonzero callback slot offsets and six variant bytes.','Selected M55 linked installer contains LE low-overhead-loop instruction unsupported by this Unicorn M4 profile; this receipt does not compare selected execution.','Callback target identity, MMIO hardware, and external producer calls remain separate gates.']}
out.write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],report['cases'])
