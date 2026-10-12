#!/usr/bin/env python3
"""Actual C/native slave advertising mode and forced-sync comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_slave_adv_start.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
uint8_t AppDbCheckBonded(void){return 0;}
void appAdvStart(uint8_t n,const uint8_t *h,const uint16_t *i,const uint16_t *d,const uint8_t *m,uint8_t c){(void)n;(void)h;(void)i;(void)d;(void)m;(void)c;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appSlaveAdvStart',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for mode,bonded in ((0,0),(1,0),(2,0),(2,1)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_subsystem_link_state_200719c8'] if is_c else 0x200719c8
   u.mem_write(state,bytes([0xa5]*0x80));u.mem_write(state+0x5d,b'\x00')
   handles=0x20080000;u.mem_write(handles,b'\x00')
   bond=(sy['AppDbCheckBonded']&~1) if is_c else 0x47a600
   start=(sy['appAdvStart']&~1) if is_c else 0x4b42f0
   calls=[]
   def hook(uc,pc,n,user):
    if pc==bond:calls.append(('bond',));uc.reg_write(UC_ARM_REG_R0,bonded)
    else:calls.append(('start',uc.reg_read(UC_ARM_REG_R0)&255,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),1)),int.from_bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP)+4,4),'little')&255))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for addr in (bond,start):u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,handles)
   u.reg_write(UC_ARM_REG_R2,0x20080010);u.reg_write(UC_ARM_REG_R3,0x20080020)
   u.reg_write(UC_ARM_REG_SP,0x200ff000)
   u.mem_write(0x200ff000,(0x20080030).to_bytes(4,'little')+(1).to_bytes(4,'little')+mode.to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['appSlaveAdvStart'] if is_c else 0x4b446a)|1,0x600000,count=3000)
   pair.append((calls,bytes(u.mem_read(state+0x40,0x40))))
  assert pair[0]==pair[1],(mode,bonded,pair)
print('PASS_BLE_APP_SLAVE_ADV_START_NATIVE 4')
