#!/usr/bin/env python3
"""Bounded stock/source value and SRAM comparison for two busy-delay bodies."""
from pathlib import Path
import hashlib
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/sensor_delay_candidate.c'
obj=HERE/'sensor_delay_candidate.o';elf=HERE/'sensor_delay_candidate.elf';ld=HERE/'sensor_delay_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
ld.write_text('SECTIONS { . = 0x00100000; .text : { *(.text*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
with elf.open('rb') as stream:
    e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
rows=[]
for address,name,inputs in [(0x0800a408,'case_binary_sensor_delay',[0,1,0xffffffff]),
                            (0x0800a148,'case_binary_sensor_delay_count',[0,1,2,0xffffffff])]:
    for input_word in inputs:
        outputs=[]
        for original in [True,False]:
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
            u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
            u.mem_map(0x00100000,0x10000)
            for a,b in segments:u.mem_write(a,b)
            u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_R0,input_word)
            u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
            u.emu_start((address if original else sym[name])|1,0x20001000,count=1000000)
            outputs.append((u.reg_read(UC_ARM_REG_PC),u.reg_read(UC_ARM_REG_R0),
                            hashlib.sha256(bytes(u.mem_read(0x20000000,0x7000))).hexdigest()))
        assert outputs[0]==outputs[1],(name,input_word,outputs)
        rows.append((name,input_word))
print('PASS_SENSOR_DELAY_BOUNDED',len(rows))
