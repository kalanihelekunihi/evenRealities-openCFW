#!/usr/bin/env python3
"""Actual C/native appSetAdvScanData fragment decisions and synced flag."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_adv_scan_data.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
void appSetAdvScanDataFrag(uint8_t h,uint8_t l){(void)h;(void)l;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appSetAdvScanData',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for mode in (0,1):
  for pattern in ((0,0),(3,0),(0,3),(3,3)):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    state=sy['audio_ble_subsystem_link_state_200719c8'] if is_c else 0x200719c8
    u.mem_write(state,bytes([0]*0x80))
    for j in range(2):
     loc=mode*2+j;u.mem_write(state+0x20+loc*2,(3).to_bytes(2,'little'))
     u.mem_write(state+0x40+loc*2,pattern[j].to_bytes(2,'little'))
    child=(sy['appSetAdvScanDataFrag']&~1) if is_c else 0x4b3416;calls=[]
    def hook(uc,pc,n,user):calls.append((uc.reg_read(UC_ARM_REG_R0)&0xff,uc.reg_read(UC_ARM_REG_R1)&0xff));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=child,end=child)
    u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,mode)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['appSetAdvScanData'] if is_c else 0x4b3514)|1,0x600000,count=1000)
    pair.append((calls,bytes(u.mem_read(state+0x55,1))))
   assert pair[0]==pair[1],(mode,pattern,pair)
print('PASS_BLE_APP_ADV_SCAN_NATIVE 8')
