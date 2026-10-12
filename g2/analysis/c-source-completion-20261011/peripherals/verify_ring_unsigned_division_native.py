#!/usr/bin/env python3
"""Compare actual ARM restoring division with native integer helper."""
from pathlib import Path
import subprocess,tempfile,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_unsigned_division.c'
rng=random.Random(0x47cc60)
cases=[(0,0,1000,0),(0xffffffff,0,1000,0),(0,1,1000,0),(0xffffffff,0xffffffff,1000,0),(123,456,0,0),(0xffffffff,0xffffffff,0xffffffff,0xffffffff)]
cases += [(rng.getrandbits(32),rng.getrandbits(32),rng.getrandbits(32)|1,rng.getrandbits(32)) for _ in range(24)]
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_u64_div_47cc60',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for arg in cases:
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),arg):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_uart_ring_u64_div_47cc60'] if compiled else 0x47cc60)|1,0x600000,count=30000)
   pair.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
  assert pair[0]==pair[1],(arg,pair)
print('PASS_RING_UNSIGNED_DIVISION_NATIVE',len(cases))
