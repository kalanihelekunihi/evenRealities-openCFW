#!/usr/bin/env python3
"""Compiled-C/stock containment and rounded-corner call order."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_render_contains.c'
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text('__attribute__((naked)) unsigned audio_uart_lv_round_corner_450dd4(){__asm volatile("bx lr");}\n');elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_area_contains_450f28',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for inner in ((1,2,8,9),(-1,2,8,9),(1,2,11,9)):
  for radius in (0,1,3):
   for fail in (0,2):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     ia=0x2007f100;oa=0x2007f200;u.mem_write(ia,struct.pack('<4i',*inner));u.mem_write(oa,struct.pack('<4i',0,0,10,10))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,ia);u.reg_write(UC_ARM_REG_R1,oa);u.reg_write(UC_ARM_REG_R2,radius)
     seen=[];addr=(sym['audio_uart_lv_round_corner_450dd4']&~1) if is_c else 0x450dd4
     def hook(uc,a,size,_):
      if a==addr:
       point=uc.reg_read(UC_ARM_REG_R1);seen.append(tuple(struct.unpack('<2i',bytes(uc.mem_read(point,8)))));uc.reg_write(UC_ARM_REG_R0,0 if len(seen)==fail else 1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook);u.emu_start((sym['audio_uart_lv_area_contains_450f28'] if is_c else 0x450f28)|1,0x600000,count=300)
     pair.append((u.reg_read(UC_ARM_REG_R0),seen))
    assert pair[0]==pair[1],(inner,radius,fail,pair)
    cases+=1
 print('PASS_DISPLAY_LV_RENDER_CONTAINS_NATIVE',cases)
