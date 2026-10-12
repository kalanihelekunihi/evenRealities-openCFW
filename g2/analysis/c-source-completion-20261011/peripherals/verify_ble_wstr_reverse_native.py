#!/usr/bin/env python3
"""Pinned Cordio reverse copy versus stock ARM 0x56d8c4."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
V=R.parent/'third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio'
S=R/'analysis/c-source-completion-20261011/peripherals/smp_tables/candidate_wstr_util.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections',
                 '-Wl,-Ttext=0x100000','-Wl,-e,WStrReverseCpy',
                 '-I'+str(R/'components/bootloader/filesystem/freestanding_include'),
                 '-I'+str(V/'wsf/sources/port/freertos'),'-I'+str(V/'wsf/sources'),
                 str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for size in (0,1,6,16,31):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   dst=0x20080000;src=0x20080100
   u.mem_write(dst,bytes([0xa5]*40));u.mem_write(src,bytes(range(40)))
   u.reg_write(UC_ARM_REG_R0,dst);u.reg_write(UC_ARM_REG_R1,src)
   u.reg_write(UC_ARM_REG_R2,size);u.reg_write(UC_ARM_REG_SP,0x200ff000)
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['WStrReverseCpy'] if compiled else 0x56d8c4)|1,0x600000,count=2000)
   pair.append(bytes(u.mem_read(dst,40)))
  assert pair[0]==pair[1],(size,pair)
print('PASS_BLE_WSTR_REVERSE_NATIVE 5')
