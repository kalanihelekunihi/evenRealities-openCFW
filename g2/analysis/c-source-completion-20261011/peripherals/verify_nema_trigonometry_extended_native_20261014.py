#!/usr/bin/env python3
"""Compare Nema sine/cosine native float bits across angle ranges."""
from pathlib import Path
import random
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_S0

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_trigonometry.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
bits=lambda value:int.from_bytes(struct.pack('<f',value),'little')
functions=(('audio_uart_nema_cos_524130',0x524130),
           ('audio_uart_nema_sin_52405c',0x52405c))
with tempfile.TemporaryDirectory() as temp:
    image=Path(temp)/'trigonometry.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4',
                    '-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard',
                    '-std=c11','-ffreestanding','-fno-builtin','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000',str(source),
                    '-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in
                 elf.get_section_by_name('.symtab').iter_symbols()}
    def run(compiled,function,degrees):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        uc.reg_write(UC_ARM_REG_S0,bits(degrees))
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        name,native=function
        uc.emu_start((symbols[name] if compiled else native)|1,
                     0x300000,count=400)
        return uc.reg_read(UC_ARM_REG_S0)
    rng=random.Random(0x524130)
    values=[float(x) for x in (-1080,-720,-540,-450,-360,-270,-180,-135,
                                 -90,-45,-1,0,1,30,45,60,90,120,135,180,
                                 270,360,450,540,720,1080)]
    values += [rng.randint(-1440,1440)/8.0 for _ in range(128)]
    values += [rng.randint(-360000,360000)/16.0 for _ in range(512)]
    for function in functions:
        for degrees in values:
            native=run(False,function,degrees)
            candidate=run(True,function,degrees)
            assert candidate==native,(function[0],degrees,hex(native),hex(candidate))
    print('PASS_NEMA_TRIGONOMETRY_NATIVE',len(values)*len(functions))
