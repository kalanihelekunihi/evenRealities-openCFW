#!/usr/bin/env python3
"""Compare Apollo matrix point outputs against native VFP instructions."""
from pathlib import Path
import random
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import (UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_R0,
                               UC_ARM_REG_R1,UC_ARM_REG_R2)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_point.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
pack=lambda values:struct.pack('<'+'f'*len(values),*values)
with tempfile.TemporaryDirectory() as temp:
    image=Path(temp)/'point.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55',
                    '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),
                    '-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        candidate=next(s['st_value'] for s in
                       elf.get_section_by_name('.symtab').iter_symbols()
                       if s.name=='audio_uart_nema_matrix_point_561ad4')
    def run(compiled,matrix,x,y):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,content in segments:uc.mem_write(address,content)
        base=0x20008000
        uc.mem_write(base,pack(matrix))
        uc.mem_write(base+0x100,pack((x,y)))
        uc.reg_write(UC_ARM_REG_R0,base)
        uc.reg_write(UC_ARM_REG_R1,base+0x100)
        uc.reg_write(UC_ARM_REG_R2,base+0x104)
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        uc.emu_start((candidate if compiled else 0x561ad4)|1,
                     0x300000,count=200)
        return bytes(uc.mem_read(base+0x100,8))
    rng=random.Random(0x561ad4)
    cases=[([1,0,0,0,1,0,0,0,1],3,4),
           ([1,2,3,4,5,6,0,0,1],-7,9),
           ([2,0,5,0,3,-4,0.25,0.125,1],10,-3)]
    for _ in range(128):
        m=[rng.randint(-32,32)/8.0 for _ in range(9)]
        m[8]=rng.choice((1.0,2.0,4.0))
        x=rng.randint(-64,64)/4.0;y=rng.randint(-64,64)/4.0
        divisor=m[6]*x+m[7]*y+m[8]
        if abs(divisor)<0.125:continue
        cases.append((m,x,y))
    for matrix,x,y in cases:
        native=run(False,matrix,x,y)
        compiled=run(True,matrix,x,y)
        assert compiled==native,(matrix,x,y,native.hex(),compiled.hex())
    print('PASS_NEMA_MATRIX_POINT_NATIVE',len(cases))
