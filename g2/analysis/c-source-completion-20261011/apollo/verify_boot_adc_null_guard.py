#!/usr/bin/env python3
"""Bounded stock/source NULL precondition for native 0x42ea68 ADC apply.

The M4 C link keeps the selected source body. The test-only clock lower is a
BKPT trap. Both stock and source must fault on the native context+4 read.
"""
from pathlib import Path
import hashlib
import subprocess
import tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R1
from unicorn import UcError, UC_ERR_READ_UNMAPPED

ROOT=Path(__file__).resolve().parents[4]
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
assert hashlib.sha256(STOCK.read_bytes()).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
SOURCE=ROOT/'g2/components/bootloader/initializer_callbacks/adc_profile.c'
with tempfile.TemporaryDirectory() as t:
    t=Path(t)
    obj=t/'adc.o';cut=t/'cut.S';cutobj=t/'cut.o';elf=t/'adc.elf';raw=t/'adc.bin'
    cut.write_text('.syntax unified\n.thumb\n.text\n.global clock_request\n.type clock_request,%function\n.thumb_func\nclock_request:\n bkpt #0\n.section .note.GNU-stack,"",%progbits\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c99','-Os','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-c',str(SOURCE),'-o',str(obj)],check=True)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-c',str(cut),'-o',str(cutobj)],check=True)
    subprocess.run(['arm-none-eabi-ld','--gc-sections','-Ttext=0x10000','-e','opencfw_bl_adc_apply_profile',str(obj),str(cutobj),'-o',str(elf)],check=True)
    subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(raw)],check=True)
    source_bytes=raw.read_bytes()
    nm=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True)
    entry=int(next(line.split()[0] for line in nm.splitlines() if line.endswith(' opencfw_bl_adc_apply_profile')),16)&~1
    for original in (True,False):
        machine=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        machine.mem_map(0x10000,0x1000);machine.mem_map(0x410000,0x25000);machine.mem_map(0x20000000,0x1000)
        machine.mem_write(0x10000,source_bytes);machine.mem_write(0x410000,STOCK.read_bytes())
        accesses=[];done=[]
        machine.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,lambda _u,kind,addr,size,value,_d:accesses.append((kind,addr,size)))
        machine.hook_add(UC_HOOK_CODE,lambda u,pc,size,_d:(done.append(True),u.emu_stop()) if pc==0x20000000 else None)
        machine.reg_write(UC_ARM_REG_SP,0x20000800);machine.reg_write(UC_ARM_REG_LR,0x20000001)
        machine.reg_write(UC_ARM_REG_R0,0);machine.reg_write(UC_ARM_REG_R1,0x20000200)
        try:
            machine.emu_start((0x42ea68 if original else entry)|1,0x20000002,count=100)
        except UcError as error:
            assert error.errno==UC_ERR_READ_UNMAPPED and not done and not any(a<0x20000000 or a>=0x40000000 for _,a,_ in accesses),(original,error,done,accesses)
            print('PASS', 'stock' if original else 'source', 'NULL faults on unmapped context+4')
        else:
            raise AssertionError((original,'expected native precondition fault'))
