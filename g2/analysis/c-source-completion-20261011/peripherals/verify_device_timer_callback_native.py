#!/usr/bin/env python3
"""Compare only stock-defined timer queue bytes in compiled ARM C/native."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_device_timer_callback.c'
STUB='''#include <stdint.h>
void audio_ble_device_manager_send(const uint8_t*p){(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_device_manager_timer_callback_4c661c',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 pair=[]
 for is_c in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  trace=[];target=sym['audio_ble_device_manager_send'] if is_c else 0x4c659a
  def hook(uc,pc,size,user):
   trace.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),4)))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sym['audio_device_manager_timer_callback_4c661c'] if is_c else 0x4c661c)|1,0x600000,count=1000)
  pair.append(trace)
 assert pair[0]==pair[1]==[b'\x02\x00\x00\x00'],pair
print('PASS_DEVICE_TIMER_CALLBACK_DEFINED_BYTES_NATIVE 1')
