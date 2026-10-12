#!/usr/bin/env python3
"""Execute stock 0x47ef18 and semantic C for every descriptor selector."""
from pathlib import Path
import subprocess,tempfile,struct,hashlib,json
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
FW=R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
B=FW.read_bytes()[32:]
SRC=R/'components/audio/power_vendor_candidate/power_descriptor_native.c'
with tempfile.TemporaryDirectory() as td:
 e=Path(td)/'descriptor.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,g2_power_get_descriptor',str(SRC),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
  sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 rows=[]
 for selector in list(range(34))+[34,35,255,256,0xffffffff]:
  for null in [False,True]:
   pair=[]
   for original in [True,False]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,b in segments:u.mem_write(a,b)
    ptr=0 if null else 0x20004000
    u.mem_write(0x20004000,b'\xa5'*16)
    u.reg_write(UC_ARM_REG_R0,ptr);u.reg_write(UC_ARM_REG_R1,selector)
    u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
    u.emu_start((0x47ef18 if original else sym['g2_power_get_descriptor'])|1,0x20001000,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20001000
    raw=bytes(u.mem_read(0x20004000,16))
    a,b,c,d=struct.unpack('<IIII',raw)
    result=(u.reg_read(UC_ARM_REG_R0), (a,c,b,d) if original else (a,b,c,d))
    pair.append(result)
   assert pair[0]==pair[1],(selector,null,pair)
   rows.append([selector,null,pair[0]])
out={'status':'PASS_POWER_DESCRIPTOR_NATIVE_C','cases':len(rows),'stock_sha256':hashlib.sha256(FW.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Semantic descriptor comparison normalizes the C struct field order against native table byte order.','ROM table address and contents are authenticated; final C linker placement remains independent.'],'rows':rows}
(Path(__file__).with_name('power-descriptor-native-comparison.json')).write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],out['cases'])
