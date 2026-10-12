#!/usr/bin/env python3
"""Compare actual compiled C/native HciDrvHandlerInit RAM writes."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_driver_handler_init.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_hci_radio_timer[16];
uint8_t audio_ble_hci_driver_secondary_timer[16];
volatile uint8_t audio_ble_hci_driver_handler_id;
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_driver_handler_init',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,value):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  a=sy['audio_ble_hci_radio_timer'] if compiled else 0x20073e64
  b=sy['audio_ble_hci_driver_secondary_timer'] if compiled else 0x20073e74
  c=sy['audio_ble_hci_driver_handler_id'] if compiled else 0x20074fcb
  u.mem_write(a,bytes([0xa5]*16));u.mem_write(b,bytes([0xa5]*16));u.mem_write(c,b'\xa5')
  u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_hci_driver_handler_init'] if compiled else 0x4b4a7c)|1,0x600000,count=100)
  return bytes(u.mem_read(a,16)),bytes(u.mem_read(b,16)),bytes(u.mem_read(c,1)),u.reg_read(UC_ARM_REG_R0)
 for v in (0,1,0x7f,0xff):
  x,y=run(False,v),run(True,v)
  assert x==y,(v,x,y)
print('PASS_HCI_DRIVER_HANDLER_INIT_NATIVE 4')
