#!/usr/bin/env python3
"""Bounded stock versus isolated selected-C Cortex-M4 SPOT installer oracle."""
from pathlib import Path
import hashlib, importlib.util, json, struct
from unicorn import arm_const as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ELF=HERE/'spot-m4-oracle/startup_runtime.elf'
_,segments,symbols=v.elf.elf_info(ELF,source_coplacement=True)
LOCAL_STOCK={
 'bl009_slot8_noop':0x42d849,'bl009_slot34_enable':0x42d693,
 'bl009_slot38_disable':0x42d6a7,'bl009_slot18_timing':0x42d5f9,
 'bl009_slot1c_config':0x42d61f,'bl009_special_slot18_timing':0x42f3db,
 'bl009_special_slot1c_config':0x42f401,'pcm21_slot14_config':0x42bd8d,
 'pcm21_slot18_timing':0x42bda1,'pcm21_slot1c_timing':0x42bdbd,
}
identity={((symbols[name]&~1)|1):stock for name,stock in LOCAL_STOCK.items()}

class Machine(v.Machine):
 def __init__(self,source):
  super().__init__(False);self.source=source
  if source:
   self.cpu.mem_map(0x435000,0x10000)
   self.exec_ranges=[]
   for segment in segments:
    start=segment['address'];self.cpu.mem_write(start,segment['data'])
    if segment['flags']&1:self.exec_ranges.append((start,start+len(segment['data'])))
  self.cpu.mem_map(0x40020000,0x3000)
  self.cpu.mem_write(0x20026e38,b'\xa5'*60)
 def code(self,uc,pc,size,user):
  callback=self.u(0x20026e38)&~1
  if callback and callback!=0xa5a5a5a4 and pc==callback:
   self.events.append(['slot0-cut',callback]);self.ret(0);return
  super().code(uc,pc,size,user)
 def invoke(self,rev,var):
  self.w(0x4002000c,rev);self.w(0x20000098,var);self.w(0x2002682c,0)
  entry=(symbols['opencfw_boot_startup_spot_dispatch']&~1) if self.source else 0x41ce52
  for r in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3):self.cpu.reg_write(r,0)
  self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1)
  self.cpu.emu_start(entry|1,v.STOP+2,count=500000)
  raw=bytes(self.cpu.mem_read(0x20026e38,60))
  slots=[]
  for i in range(0,60,4):
   pointer=struct.unpack_from('<I',raw,i)[0]
   slots.append(identity.get(pointer,pointer) if self.source else pointer)
  return {'slots':slots,'flags':bytes(self.cpu.mem_read(0x200271a9,6)).hex(),
          'mmio28':self.u(0x40020028),'mmio60':self.u(0x40020060),
          'result':self.cpu.reg_read(a.UC_ARM_REG_R0)}

rows=[]
for rev in (33,34,35,36):
 for var in (0,1,2,3):
  stock=Machine(False).invoke(rev,var)
  source=Machine(True).invoke(rev,var)
  rows.append({'rev':rev,'variant':var,'equal':stock==source,'stock':stock,'source':source})
report={'status':'PASS_COMPILED_M4_SOURCE_VS_STOCK' if all(row['equal'] for row in rows) else 'FAIL_COMPILED_M4_SOURCE_VS_STOCK',
        'cases':len(rows),'results':rows,
        'selected_source_sha256':hashlib.sha256((ROOT/'g2/components/bootloader/initializer_callbacks/startup_runtime.c').read_bytes()).hexdigest(),
        'isolated_elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),
        'limits':['Isolated selected C compiled Cortex-M4/O2; this is not the actual Cortex-M55 selected ELF or hardware.',
                  'External named callback addresses are link-time stock identities; local static callback identities are normalized by ELF symbol.',
                  'Slot-zero callback execution is cut to a zero return in both runs; callback bodies and physical MMIO are not qualified.']}
out=HERE/'boot-spot-installer-compiled-m4-oracle.json';out.write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],sum(row['equal'] for row in rows),'/',len(rows))
