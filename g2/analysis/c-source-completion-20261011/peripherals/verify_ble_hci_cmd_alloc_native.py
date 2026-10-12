#!/usr/bin/env python3
"""Actual C/native HCI command allocation and header effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_cmd_public.c'
STUB='''#include <stdint.h>
uint8_t *WsfMsgAlloc(uint16_t n){(void)n;return 0;}
void audio_ble_hci_cmd_send(void *m){(void)m;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,hciCmdAlloc',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for allocate in (False,True):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   command=0x20080000;u.mem_write(command,bytes([0xa5]*32))
   calls=[];child=(sy['WsfMsgAlloc']&~1) if compiled else 0x4bf99e
   def hook(uc,pc,n,user):
    calls.append(uc.reg_read(UC_ARM_REG_R0))
    uc.reg_write(UC_ARM_REG_R0,command if allocate else 0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=child,end=child)
   u.reg_write(UC_ARM_REG_R0,0x2019);u.reg_write(UC_ARM_REG_R1,0x1c)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['hciCmdAlloc'] if compiled else 0x52ae38)|1,0x600000,count=500)
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(command,32)),calls))
  assert pair[0]==pair[1],(allocate,pair)
print('PASS_BLE_HCI_CMD_ALLOC_NATIVE 2')
