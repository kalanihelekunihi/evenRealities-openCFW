#!/usr/bin/env python3
"""Compare Nema matrix copy, including sequential overlap behavior."""
from pathlib import Path
import random
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_R0,UC_ARM_REG_R1

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_copy.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as temp:
    image=Path(temp)/'copy.elf'
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
                       if s.name=='audio_uart_nema_matrix_copy_561830')
    def run(compiled,offset,data):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,content in segments:uc.mem_write(address,content)
        base=0x20008000
        uc.mem_write(base,data)
        uc.reg_write(UC_ARM_REG_R0,base+64+offset)
        uc.reg_write(UC_ARM_REG_R1,base+64)
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        uc.emu_start((candidate if compiled else 0x561830)|1,
                     0x300000,count=100)
        return bytes(uc.mem_read(base,len(data)))
    rng=random.Random(0x561830)
    offsets=(-40,-36,-32,-16,-4,0,4,16,32,36,40)
    cases=0
    for offset in offsets:
        for _ in range(16):
            data=rng.randbytes(160)
            native=run(False,offset,data)
            compiled=run(True,offset,data)
            assert compiled==native,(offset,data.hex(),native.hex(),compiled.hex())
            cases+=1
    print('PASS_NEMA_MATRIX_COPY_NATIVE',cases)
