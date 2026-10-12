#!/usr/bin/env python3
"""Actual ARM/C LV event-list callback, nested, stop and compaction effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_event_list_dispatch.c'
ns=['audio_uart_lv_event_count_450388','audio_uart_lv_event_slot_450390','audio_uart_lv_event_descriptor_invalid_45037e','audio_uart_lv_event_restore_4502e0','audio_uart_lv_event_compact_450346']
stub='#include <stdint.h>\n'+''.join('__attribute__((naked)) uint32_t '+n+'(){__asm volatile("bx lr");}\n' for n in ns)
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_event_list_dispatch_44ffe6',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for oldflag in (0,1):
  for callback_mode in ('none','normal','stop','cancel'):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    li=0x2007f100;ev=0x2007f200;desc=0x2007f300;slot=0x2007f400
    u.mem_write(li,b'\0'*32);u.mem_write(li+0x14,bytes([oldflag]));u.mem_write(ev,b'\0'*28);u.mem_write(ev+8,struct.pack('<I',0x38));u.mem_write(desc,struct.pack('<III',0 if callback_mode=='none' else 0x100801,0x1234,0x38));u.mem_write(slot,struct.pack('<I',desc))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,li);u.reg_write(UC_ARM_REG_R1,ev);u.reg_write(UC_ARM_REG_R2,0)
    seen=[];natives=[0x450388,0x450390,0x45037e,0x4502e0,0x450346];maps={a:i for i,a in enumerate(natives if not is_c else [sym[n]&~1 for n in ns])}
    def hook(uc,a,size,_):
     if a==0x100800:
      seen.append(('callback',bytes(uc.mem_read(ev,28))));flag=2 if callback_mode=='stop' else 1 if callback_mode=='cancel' else 0;uc.mem_write(ev+0x18,bytes([flag]));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in maps:
      i=maps[a];seen.append((i,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if i==1 else 0));uc.reg_write(UC_ARM_REG_R0,1 if i==0 else slot if i==1 else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_uart_lv_event_list_dispatch_44ffe6'] if is_c else 0x44ffe6)|1,0x600000,count=250)
    pair.append((seen,u.reg_read(UC_ARM_REG_R0)&0xff,bytes(u.mem_read(li,32)),bytes(u.mem_read(ev,28))))
   assert pair[0]==pair[1],(oldflag,callback_mode,pair)
   cases+=1
 print('PASS_DISPLAY_LV_EVENT_LIST_DISPATCH_NATIVE',cases)
