#!/usr/bin/env python3
"""Actual C/native HCI LE read-remote-features command payload and send."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_read_remote_features.c'
STUB='''#include <stdint.h>
uint8_t *hciCmdAlloc(uint16_t o,uint8_t l){(void)o;(void)l;return 0;}
void hciCmdSend(uint8_t *p){(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,HciLeReadRemoteFeatCmd',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for allocated in (False,True):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   handle=0x1234;cmd=0x20080100;u.mem_write(cmd,bytes([0xa5]*12))
   alloc=(sy['hciCmdAlloc']&~1) if is_c else 0x52ae38
   send=(sy['hciCmdSend']&~1) if is_c else 0x52ae5e
   calls=[]
   def hook(uc,pc,n,user):
    if pc==alloc:calls.append(('alloc',uc.reg_read(UC_ARM_REG_R0)&0xffff,uc.reg_read(UC_ARM_REG_R1)&255));uc.reg_write(UC_ARM_REG_R0,cmd if allocated else 0)
    else:calls.append(('send',uc.reg_read(UC_ARM_REG_R0)==cmd))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in (alloc,send):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,handle);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['HciLeReadRemoteFeatCmd'] if is_c else 0x52b352)|1,0x600000,count=1000)
   pair.append((calls,bytes(u.mem_read(cmd,12))))
  assert pair[0]==pair[1],(allocated,pair)
print('PASS_BLE_HCI_READ_REMOTE_FEATURES_NATIVE 2')
