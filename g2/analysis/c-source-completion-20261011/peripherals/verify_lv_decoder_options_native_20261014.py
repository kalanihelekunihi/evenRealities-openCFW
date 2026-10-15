#!/usr/bin/env python3
"""Compare Apollo source classifier and default option clear against C."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decoder_options.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
    image=Path(directory)/'options.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000',str(source),'-o',str(image)],
                   check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(segment['p_vaddr'],segment.data()) for segment in elf.iter_segments()
                  if segment['p_type']=='PT_LOAD']
        symbols={sym.name:sym['st_value']
                 for sym in elf.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled,kind,value):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        buf=0x20005000;uc.mem_write(buf,bytes([value&255])+bytes([0xa5]*31))
        calls=[]
        def hook(emu,address,size,user):
            r=[emu.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
            calls.append(tuple(r))
            emu.mem_write(r[0],bytes([r[2]&255])*r[1])
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        if not compiled:uc.hook_add(UC_HOOK_CODE,hook,begin=0x43c0ec,end=0x43c0ec)
        uc.reg_write(UC_ARM_REG_SP,0x200ff000);uc.reg_write(UC_ARM_REG_LR,0x600001)
        uc.reg_write(UC_ARM_REG_R0,buf if kind=='clear' or value>=0 else 0)
        uc.reg_write(UC_ARM_REG_R1,value if kind=='clear' else 0)
        if kind=='classify':
            entry=symbols['audio_uart_lv_image_source_type_488cb8'] if compiled else 0x488cb8
        else:
            entry=symbols['audio_uart_lv_decoder_default_options_4d4ccc'] if compiled else 0x4d4ccc
        uc.emu_start(entry|1,0x600000,count=60)
        return uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(buf,32)),calls

    cases=0
    for value in (-1,*range(256)):
        native=run(False,'classify',value);candidate=run(True,'classify',value)
        assert native==candidate,(value,native,candidate);cases+=1
    for size in range(17):
        native=run(False,'clear',size);candidate=run(True,'clear',size)
        assert native[1]==candidate[1],(size,native,candidate);cases+=1
    print('PASS_LV_DECODER_OPTIONS_NATIVE',cases)
