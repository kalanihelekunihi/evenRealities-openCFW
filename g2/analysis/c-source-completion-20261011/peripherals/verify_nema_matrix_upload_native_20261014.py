#!/usr/bin/env python3
"""Compare Nema matrix upload branch, normalization, and command words."""
from pathlib import Path
import random
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP,
                               UC_ARM_REG_R0)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_upload.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
pack=lambda values:struct.pack('<'+'f'*len(values),*values)
with tempfile.TemporaryDirectory() as temp:
    stub=Path(temp)/'lower.c'
    stub.write_text('void *audio_uart_nema_cl_get_space_514aec(unsigned n)'
                    '{return (void*)0;}\n')
    image=Path(temp)/'upload.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55',
                    '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),
                    str(stub),'-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in
                 elf.get_section_by_name('.symtab').iter_symbols()}
    def run(compiled,matrix,allocate):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,content in segments:uc.mem_write(address,content)
        ptr=0x20008000;command=0x20009000
        uc.mem_write(ptr,pack(matrix));uc.mem_write(command,b'\xa5'*80)
        trace=[]
        target=(symbols['audio_uart_nema_cl_get_space_514aec']&~1
                if compiled else 0x514aec)
        def hook(emu,address,size,user):
            if address!=target:return
            trace.append(emu.reg_read(UC_ARM_REG_R0))
            emu.reg_write(UC_ARM_REG_R0,command if allocate else 0)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        uc.hook_add(UC_HOOK_CODE,hook)
        uc.reg_write(UC_ARM_REG_R0,ptr)
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        start=(symbols['audio_uart_nema_matrix_upload_5226e8'] if compiled
               else 0x5226e8)
        uc.emu_start(start|1,0x300000,count=350)
        return bytes(uc.mem_read(ptr,36)),bytes(uc.mem_read(command,80)),trace
    rng=random.Random(0x5226e8)
    cases=[[1,0,0,0,1,0,0,0,1],
           [2,3,4,5,6,7,0,0,2],
           [1,2,3,4,5,6,0.25,0,1],
           [1,2,3,4,5,6,0,0.5,1],
           [1,2,3,4,5,6,0,0,0],
           [1,2,3,4,5,6,0.00000005,0,1],
           [1,2,3,4,5,6,-0.00000005,0,1]]
    cases += [[rng.randint(-32,32)/8.0 for _ in range(6)]+
              [rng.choice((0.0,0.25,-0.25)),
               rng.choice((0.0,0.25,-0.25)),
               rng.choice((1.0,2.0,4.0))] for _ in range(64)]
    count=0
    for matrix in cases:
        for allocate in (False,True):
            native=run(False,matrix,allocate)
            candidate=run(True,matrix,allocate)
            assert candidate==native,(matrix,allocate,native,candidate)
            count+=1
    print('PASS_NEMA_MATRIX_UPLOAD_NATIVE',count)
