#!/usr/bin/env python3
"""Actual C/native ATT database CMAC request ABI and return."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_atts_hash_string.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_att_common_state[0x64];
uint8_t SecCmac(uint8_t*k,uint8_t*m,uint16_t n,uint8_t h,uint16_t p,uint8_t e){(void)k;(void)m;(void)n;(void)h;(void)p;(void)e;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,AttsHashDatabaseString',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for length in (0,31,0x101):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_att_common_state'] if compiled else 0x200610ac
   u.mem_write(state+0x60,b'\x17')
   key,msg=0x20080000,0x20080100;calls=[]
   child=(sy['SecCmac']&~1) if compiled else 0x53665c
   def hook(uc,pc,n,user):
    sp=uc.reg_read(UC_ARM_REG_SP)
    extra=[int.from_bytes(uc.mem_read(sp+i,4),'little') for i in (0,4)]
    calls.append(tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))+tuple(extra))
    uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=child,end=child)
   u.reg_write(UC_ARM_REG_R0,key);u.reg_write(UC_ARM_REG_R1,msg);u.reg_write(UC_ARM_REG_R2,length)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['AttsHashDatabaseString'] if compiled else 0x53525c)|1,0x600000,count=1000)
   pair.append((u.reg_read(UC_ARM_REG_R0),calls))
  assert pair[0]==pair[1],(length,pair)
print('PASS_BLE_ATTS_HASH_STRING_NATIVE 3')
