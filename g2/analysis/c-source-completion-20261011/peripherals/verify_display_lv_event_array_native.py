#!/usr/bin/env python3
"""Actual ARM/C LV event descriptor count, slot and disabled flag."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_event_array.c'
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text('__attribute__((naked)) void audio_uart_lvgl_log(){__asm volatile("bx lr");}\n');elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_event_count_450388',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,nat in [('audio_uart_lv_event_count_450388',0x450388),('audio_uart_lv_event_slot_450390',0x450390),('audio_uart_lv_event_descriptor_invalid_45037e',0x45037e)]:
  for index in (0,1,2):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    li=0x2007f100;data=0x2007f200;u.mem_write(li,struct.pack('<IIII',data,2,2,4)+b'\0'*8);u.mem_write(data,b'\0'*32);u.mem_write(li+8,struct.pack('<I',0x10000 if index else 0))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,li);u.reg_write(UC_ARM_REG_R1,index)
    u.emu_start((sym[name] if is_c else nat)|1,0x600000,count=100)
    pair.append(u.reg_read(UC_ARM_REG_R0))
   assert pair[0]==pair[1],(name,index,pair)
   cases+=1
 print('PASS_DISPLAY_LV_EVENT_ARRAY_NATIVE',cases)
