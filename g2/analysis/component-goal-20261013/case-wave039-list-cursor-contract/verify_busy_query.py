#!/usr/bin/env python3
"""Reachable real query/conversion path while native bus guard is busy."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
import hashlib,json,struct
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;elf=H/'measurement-fixture.elf';fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
rows=[]
for name in ['case_boot_battery_percent','case_init_read_product_byte']:
 for sentinel in [0,19,0xdeadbeef,0xffffffff]:
  pair=[]
  for native in [True,False]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
   if native:u.mem_write(0x08000000,fw.read_bytes()[32:])
   else:
    for a,b in segs:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000029,b'\x01');u.mem_write(0x20004000,struct.pack('<I',sentinel));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x2000f001)
   u.emu_start((0x08009ebc if native else sym[name])|1,0x2000f000,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x2000f000 and u.reg_read(UC_ARM_REG_SP)==0x20008000;pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20004000,4)),bytes(u.mem_read(0x20000000,0x3000))))
  assert pair[0]==pair[1] and pair[0][0]==0 and pair[0][1]==bytes(4);rows.append({'symbol':name,'initial_output':sentinel,'status':0,'percentage':0})
r={'status':'PASS_FULL_NATIVE_C_BUSY_QUERY_AND_CONVERSION','cases':len(rows),'ELF_sha256':sha(elf),'firmware_sha256':sha(fw),'comparisons':rows,'child_stubs_or_cuts':False,'limits':['Actual guarded query/status wrapper, realdelay loops and actual divide/conversion execute. Busy guard stays1 in a coherent single-thread fixture; no sensorbus/MMIO model orphysicaltiming claim.','Does not validate guard release races, device data transfers or sensorfailure effects.']};(H/'busy-query-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
