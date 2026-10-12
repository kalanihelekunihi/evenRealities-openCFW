#!/usr/bin/env python3
"""Actual C/native advertising data setter and app-state comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_adv_data.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
int appSlaveAdvMode(void){return 0;}
void appSetAdvScanDataFrag(uint8_t h,uint8_t l){(void)h;(void)l;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,AppAdvSetData',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for enabled,length in ((0,40),(1,0),(1,31),(1,40)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_subsystem_link_state_200719c8'] if is_c else 0x200719c8
   u.mem_write(state,bytes([0]*0x80));u.mem_write(state+0x57,b'\x03')
   data=0x20080000;u.mem_write(data,bytes([i&255 for i in range(64)]))
   mode=(sy['appSlaveAdvMode']&~1) if is_c else 0x4b2bde
   lower=(sy['appAdvSetData']&~1) if is_c else 0x4b4240
   calls=[]
   def hook(uc,pc,n,user):
    if pc==mode:uc.reg_write(UC_ARM_REG_R0,enabled)
    else:
     sp=uc.reg_read(UC_ARM_REG_SP)
     calls.append((uc.reg_read(UC_ARM_REG_R0)&255,uc.reg_read(UC_ARM_REG_R1)&255,uc.reg_read(UC_ARM_REG_R2)&0xffff,uc.reg_read(UC_ARM_REG_R3)==data,int.from_bytes(uc.mem_read(sp,4),'little')&0xffff,int.from_bytes(uc.mem_read(sp+4,4),'little')&0xffff))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in (mode,lower):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,2);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_R2,data)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['AppAdvSetData'] if is_c else 0x4b2cec)|1,0x600000,count=1000)
   pair.append(calls)
  assert pair[0]==pair[1],(enabled,length,pair)
 for stateval,length in ((3,5),(0,5),(0,251),(0,252)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_subsystem_link_state_200719c8'] if is_c else 0x200719c8
   u.mem_write(state,bytes([0]*0x80));u.mem_write(state+0x57,bytes([stateval]))
   data=0x20080000;child=(sy['appSetAdvScanDataFrag']&~1) if is_c else 0x4b3416;calls=[]
   def hook(uc,pc,n,user):calls.append((uc.reg_read(UC_ARM_REG_R0)&255,uc.reg_read(UC_ARM_REG_R1)&255));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=child,end=child)
   u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_R2,length);u.reg_write(UC_ARM_REG_R3,data)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,(31).to_bytes(4,'little')+(31).to_bytes(4,'little'));u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['appAdvSetData'] if is_c else 0x4b4240)|1,0x600000,count=1000)
   pair.append((calls,bytes(u.mem_read(state,0x60))))
  assert pair[0]==pair[1],(stateval,length)
print('PASS_BLE_APP_ADV_DATA_NATIVE 8')
