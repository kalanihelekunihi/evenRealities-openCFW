#!/usr/bin/env python3
"""Compare Nema matrix translation direct memory effects."""
from pathlib import Path
import random
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import (UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_R0,
                               UC_ARM_REG_S0,UC_ARM_REG_S1)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_translate.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
pack=lambda values:struct.pack('<'+'f'*len(values),*values)
bits=lambda value:int.from_bytes(pack((value,)),'little')
with tempfile.TemporaryDirectory() as temp:
    image=Path(temp)/'translate.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4',
                    '-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard',
                    '-std=c11','-ffreestanding','-fno-builtin','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000',str(source),
                    '-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        candidate=next(s['st_value'] for s in
                       elf.get_section_by_name('.symtab').iter_symbols()
                       if s.name=='audio_uart_nema_matrix_translate_561856')
    def run(compiled,matrix,x,y):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,content in segments:uc.mem_write(address,content)
        ptr=0x20008000
        uc.mem_write(ptr,pack(matrix))
        uc.reg_write(UC_ARM_REG_R0,ptr)
        uc.reg_write(UC_ARM_REG_S0,bits(x))
        uc.reg_write(UC_ARM_REG_S1,bits(y))
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        uc.emu_start((candidate if compiled else 0x561856)|1,
                     0x300000,count=150)
        return bytes(uc.mem_read(ptr,36))
    rng=random.Random(0x561856)
    cases=[([1,0,0,0,1,0,0,0,1],3,4),
           ([1,2,3,4,5,6,7,8,9],-2,0.5)]
    cases += [([rng.randint(-64,64)/8.0 for _ in range(9)],
               rng.randint(-16,16)/4.0,rng.randint(-16,16)/4.0)
              for _ in range(128)]
    for matrix,x,y in cases:
        native=run(False,matrix,x,y)
        compiled=run(True,matrix,x,y)
        assert compiled==native,(matrix,x,y,native.hex(),compiled.hex())
    print('PASS_NEMA_MATRIX_TRANSLATE_NATIVE',len(cases))
