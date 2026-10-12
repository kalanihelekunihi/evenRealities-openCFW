#!/usr/bin/env python3
"""Bounded compiled C/native comparison of appAdvStop state and DM effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_adv_stop.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
uint8_t audio_ble_app_adv_state(void){for(uint8_t i=0;i<2;i++)if(audio_ble_subsystem_link_state_200719c8[0x57+i]<3)return 1;return 0;}
void DmAdvStop(uint8_t n,const uint8_t *h){(void)n;(void)h;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appAdvStop',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for count,initial in ((0,(0,2)),(1,(2,3)),(2,(0,1))):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_subsystem_link_state_200719c8'] if compiled else 0x200719c8
   handles=0x20080000;u.mem_write(handles,b'\x00\x01')
   u.mem_write(state+0x57,bytes(initial));u.mem_write(state+0x5d,b'\x07')
   child=(sy['DmAdvStop']&~1) if compiled else 0x4b3250
   calls=[]
   def hook(uc,pc,n,user):
    calls.append((uc.reg_read(UC_ARM_REG_R0)&0xff,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),count))))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=child,end=child)
   u.reg_write(UC_ARM_REG_R0,count);u.reg_write(UC_ARM_REG_R1,handles)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['appAdvStop'] if compiled else 0x4b43fc)|1,0x600000,count=1000)
   pair.append((bytes(u.mem_read(state+0x57,2)),bytes(u.mem_read(state+0x5d,1)),calls))
  assert pair[0]==pair[1],(count,initial,pair)
print('PASS_BLE_APP_ADV_STOP_NATIVE 3')
