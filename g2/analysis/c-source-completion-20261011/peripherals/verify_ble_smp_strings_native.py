#!/usr/bin/env python3
"""Actual ARM C/native SMP string mapper comparison for every byte input."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text('#include <stdint.h>\nuint8_t audio_ble_smp_handler_state[0xfc];\n')
 elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,smpEventStr',str(S/'display_ble_smp_strings.c'),
                 str(S/'display_ble_smp_state_strings.c'),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def engine(compiled):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
  u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  return u
 native,compiled=engine(False),engine(True)
 for fn,address in [('smpEventStr',0x56d31e),('smpiStateStr',0x537f24),('smprStateStr',0x538114)]:
  for v in range(256):
   pair=[]
   for u,start in ((native,address),(compiled,sym[fn])):
    u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_SP,0x200ff000)
    u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start(start|1,0x600000,count=1000)
    p=u.reg_read(UC_ARM_REG_R0);s=bytearray()
    for n in range(100):
     c=u.mem_read(p+n,1)[0]
     if c==0:break
     s.append(c)
    pair.append(bytes(s))
   assert pair[0]==pair[1],(fn,v,pair)
print('PASS_BLE_SMP_STRINGS_NATIVE 768')
