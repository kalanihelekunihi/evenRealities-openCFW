#!/usr/bin/env python3
"""Actual compiled-C/native connectability and role-count comparisons."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_adv_capacity.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
uint8_t audio_ble_discovery_connection_records_200717b0[0x90];
uint8_t DmConnRole(uint8_t c){(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appSlaveConnectableAdv',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for typ,handle in ((0,0),(4,0),(5,1),(2,1),(0,3)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_subsystem_link_state_200719c8'] if is_c else 0x200719c8
   u.mem_write(state+0x59,bytes([typ,typ]));u.mem_write(0x20080000,bytes([handle]))
   u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,0x20080000)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['appSlaveConnectableAdv'] if is_c else 0x4b32e2)|1,0x600000,count=1000)
   pair.append(u.reg_read(UC_ARM_REG_R0)&255)
  assert pair[0]==pair[1],(typ,handle,pair)
 for role in (0,1):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   rows=sy['audio_ble_discovery_connection_records_200717b0'] if is_c else 0x200717b0
   for i,c in enumerate((1,2,0)):u.mem_write(rows+i*0x30+4,bytes([c]))
   child=(sy['DmConnRole']&~1) if is_c else 0x4b73c4;calls=[]
   def hook(uc,pc,n,user):
    c=uc.reg_read(UC_ARM_REG_R0)&255;calls.append(c);uc.reg_write(UC_ARM_REG_R0,c&1)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=child,end=child)
   u.reg_write(UC_ARM_REG_R0,role);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['appNumConns'] if is_c else 0x4bacf0)|1,0x600000,count=1000)
   pair.append((u.reg_read(UC_ARM_REG_R0)&255,calls))
  assert pair[0]==pair[1],(role,pair)
print('PASS_BLE_APP_ADV_CAPACITY_NATIVE 7')
