#!/usr/bin/env python3
"""Actual C/native advertising fragmentation and offset effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_adv_scan_frag.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
void DmAdvSetData(uint8_t h,uint8_t o,uint8_t l,uint8_t n,const uint8_t *p){(void)h;(void)o;(void)l;(void)n;(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appSetAdvScanDataFrag',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for location in (0,1):
  for remaining in (0,5,251,252,500):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    state=sy['audio_ble_subsystem_link_state_200719c8'] if is_c else 0x200719c8
    data=0x20080000;u.mem_write(data,bytes([j&255 for j in range(600)]))
    u.mem_write(state,bytes([0]*0x80));u.mem_write(state+location*4,data.to_bytes(4,'little'))
    u.mem_write(state+0x20+location*2,remaining.to_bytes(2,'little'))
    u.mem_write(state+0x50,(600).to_bytes(2,'little'))
    child=(sy['DmAdvSetData']&~1) if is_c else 0x4b319e;calls=[]
    def hook(uc,pc,n,user):
     sp=uc.reg_read(UC_ARM_REG_SP);p=int.from_bytes(uc.mem_read(sp,4),'little')
     calls.append((uc.reg_read(UC_ARM_REG_R0)&255,uc.reg_read(UC_ARM_REG_R1)&255,uc.reg_read(UC_ARM_REG_R2)&255,uc.reg_read(UC_ARM_REG_R3)&255,p-data))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=child,end=child)
    u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,location)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['appSetAdvScanDataFrag'] if is_c else 0x4b3416)|1,0x600000,count=4000)
    pair.append((calls,bytes(u.mem_read(state+0x40+location*2,2))))
   assert pair[0]==pair[1],(location,remaining,pair)
print('PASS_BLE_APP_ADV_SCAN_FRAG_NATIVE 10')
