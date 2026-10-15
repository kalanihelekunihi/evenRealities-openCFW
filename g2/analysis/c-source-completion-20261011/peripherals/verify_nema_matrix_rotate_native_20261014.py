#!/usr/bin/env python3
"""Compare matrix rotation call order and matrix writes with native."""
from pathlib import Path
import random
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP,
                               UC_ARM_REG_R0,UC_ARM_REG_S0)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_rotate.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
pack=lambda values:struct.pack('<'+'f'*len(values),*values)
bits=lambda value:int.from_bytes(pack((value,)),'little')
lower=(('audio_uart_nema_cos_524130',0x524130),
       ('audio_uart_nema_sin_52405c',0x52405c))
with tempfile.TemporaryDirectory() as temp:
    stub=Path(temp)/'lower.c'
    stub.write_text('\n'.join(
        f'float {name}(float a) __attribute__((pcs("aapcs-vfp")));\n'
        f'float {name}(float a){{return 0;}}' for name,_ in lower))
    image=Path(temp)/'rotate.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4',
                    '-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard',
                    '-std=c11','-ffreestanding','-fno-builtin','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000',str(source),str(stub),
                    '-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in
                 elf.get_section_by_name('.symtab').iter_symbols()}
    def run(compiled,matrix,angle):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,content in segments:uc.mem_write(address,content)
        ptr=0x20008000
        uc.mem_write(ptr,pack(matrix))
        trace=[]
        def hook(emu,address,size,user):
            for name,native in lower:
                target=(symbols[name]&~1) if compiled else native
                if address!=target:continue
                trace.append((name,emu.reg_read(UC_ARM_REG_S0)))
                response=(0.75+angle/32 if name==lower[0][0]
                          else 0.25-angle/64)
                emu.reg_write(UC_ARM_REG_S0,bits(response))
                emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
                return
        uc.hook_add(UC_HOOK_CODE,hook)
        uc.reg_write(UC_ARM_REG_R0,ptr)
        uc.reg_write(UC_ARM_REG_S0,bits(angle))
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        start=(symbols['audio_uart_nema_matrix_rotate_561964'] if compiled
               else 0x561964)
        uc.emu_start(start|1,0x300000,count=250)
        return bytes(uc.mem_read(ptr,36)),trace
    rng=random.Random(0x561964)
    cases=[([1,0,0,0,1,0,0,0,1],0),
           ([1,2,3,4,5,6,7,8,9],-2)]
    cases += [([rng.randint(-64,64)/8.0 for _ in range(9)],
               rng.randint(-16,16)/4.0) for _ in range(128)]
    for matrix,angle in cases:
        native=run(False,matrix,angle)
        candidate=run(True,matrix,angle)
        assert candidate==native,(matrix,angle,native,candidate)
    print('PASS_NEMA_MATRIX_ROTATE_NATIVE',len(cases))
