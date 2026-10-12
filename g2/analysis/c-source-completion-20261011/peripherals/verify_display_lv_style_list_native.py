#!/usr/bin/env python3
"""Actual ARM/C intrusive LV list access and head/middle/tail removal."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_list.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_list_remove_482c0e',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for count in (1,3):
  for which in range(count):
   for op in ('first','next','remove'):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     li=0x2007f100;nodes=[0x2007f200,0x2007f300,0x2007f400][:count]
     u.mem_write(li,struct.pack('<III',0,nodes[0],nodes[-1]))
     for i,n in enumerate(nodes):u.mem_write(n,struct.pack('<II',nodes[i-1] if i else 0,nodes[i+1] if i+1<count else 0))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,li);u.reg_write(UC_ARM_REG_R1,nodes[which])
     nat,name={'first':(0x482ce4,'audio_uart_lv_list_first_482ce4'),'next':(0x482cfa,'audio_uart_lv_list_next_482cfa'),'remove':(0x482c0e,'audio_uart_lv_list_remove_482c0e')}[op]
     u.emu_start((sym[name] if is_c else nat)|1,0x600000,count=120)
     pair.append((u.reg_read(UC_ARM_REG_R0) if op!='remove' else 0,bytes(u.mem_read(li,12)),[bytes(u.mem_read(n,8)) for n in nodes]))
    assert pair[0]==pair[1],(count,which,op,pair)
    cases+=1
 print('PASS_DISPLAY_LV_STYLE_LIST_NATIVE',cases)
