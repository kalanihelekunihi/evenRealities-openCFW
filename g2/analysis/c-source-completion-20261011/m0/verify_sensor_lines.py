#!/usr/bin/env python3
"""Compare original and source line-helper arguments at GPIO writer entry."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/sensor_line_candidate.c'
obj=HERE/'sensor_line_candidate.o';elf=HERE/'sensor_line_candidate.elf';ld=HERE/'sensor_line_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
ld.write_text('case_control_write = 0x0010f001; SECTIONS { . = 0x00100000; .text : { *(.text*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
with elf.open('rb') as stream:
    e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
rows=[]
for name,entry in [('case_binary_sensor_line_a',0x0800a550),('case_binary_sensor_line_b',0x0800a574)]:
    for selector in [0,1,0xff]:
        for level in [0,1,0xffffffff]:
            pair=[]
            for original in [True,False]:
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
                u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
                u.mem_map(0x00100000,0x10000)
                for a,b in segments:u.mem_write(a,b)
                u.mem_map(0x20000000,0x10000);u.mem_write(0x20000114,bytes([selector]))
                u.reg_write(UC_ARM_REG_R0,level);u.reg_write(UC_ARM_REG_SP,0x20008000)
                u.reg_write(UC_ARM_REG_LR,0x20001001)
                calls=[]
                def hook(uc,address,size,user):
                    if address in [0x08004e9e,0x0010f000]:
                        calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)))
                        uc.emu_stop()
                u.hook_add(UC_HOOK_CODE,hook)
                u.emu_start((entry if original else sym[name])|1,0x20001000,count=1000)
                assert len(calls)==1,(name,selector,level,original,calls)
                pair.append(calls[0])
            assert pair[0]==pair[1],(name,selector,level,pair)
            rows.append((name,selector,level))
print('PASS_SENSOR_LINES_TO_GPIO',len(rows))
