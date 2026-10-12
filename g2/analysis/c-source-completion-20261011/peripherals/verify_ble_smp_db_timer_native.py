#!/usr/bin/env python3
"""Actual C/native SMP DB timer active/inactive effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_db_service_timer.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_smp_database[0x110];
void WsfTimerStartMs(void*t,uint32_t n){(void)t;(void)n;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,smpDbStartServiceTimer',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for active in (0,1):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   base=sy['audio_ble_smp_database'] if compiled else 0x200708ec
   u.mem_write(base+0xfd,bytes([active]));calls=[]
   child=(sy['WsfTimerStartMs']&~1) if compiled else 0x52a4c4
   def hook(uc,pc,n,user):
    calls.append((uc.reg_read(UC_ARM_REG_R0)-base,uc.reg_read(UC_ARM_REG_R1)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=child,end=child)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['smpDbStartServiceTimer'] if compiled else 0x541e34)|1,0x600000,count=1000)
   pair.append(calls)
  assert pair[0]==pair[1],(active,pair)
print('PASS_BLE_SMP_DB_TIMER_NATIVE 2')
