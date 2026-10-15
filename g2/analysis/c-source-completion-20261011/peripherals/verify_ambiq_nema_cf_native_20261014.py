#!/usr/bin/env python3
"""Exhaustive byte-domain comparison of Apollo Nema format conversion."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_R0

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_cf.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as temp:
    image=Path(temp)/'nema_cf.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55',
                    '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),
                    '-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        sym=next(s for s in elf.get_section_by_name('.symtab').iter_symbols()
                 if s.name=='audio_uart_ambiq_nema_cf_4b05a4')
        candidate=sym['st_value']
    def run(compiled,value):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        uc.reg_write(UC_ARM_REG_R0,value)
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        uc.emu_start((candidate if compiled else 0x4b05a4)|1,0x300000,count=100)
        return uc.reg_read(UC_ARM_REG_R0)
    for value in range(256):
        assert run(True,value)==run(False,value),value
    for value in (0x100,0x10e,0x10014,0xffffffff):
        assert run(True,value)==run(False,value),value
    print('PASS_AMBIQ_NEMA_CF_NATIVE',260)
