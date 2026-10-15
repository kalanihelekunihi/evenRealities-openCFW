#!/usr/bin/env python3
"""Compare source stencil state transitions with Apollo native instructions."""
from pathlib import Path
import itertools
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import (UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_SP,
                               UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/stencil.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as temp:
    stub=Path(temp)/'cell.c'
    stub.write_text('volatile unsigned audio_uart_nema_context_cell[1];\n')
    image=Path(temp)/'stencil.elf'
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

    def run(compiled,inputs,initial):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000)
        uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000)
        uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        cell=(symbols['audio_uart_nema_context_cell'] if compiled
              else 0x20074efc)
        context=0x20008000
        uc.mem_write(cell,context.to_bytes(4,'little'))
        for index,value in enumerate(initial):
            uc.mem_write(context+index*4,value.to_bytes(4,'little'))
        start=(symbols['audio_uart_nema_stencil_save_52266e'] if compiled
               else 0x52266e)
        for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,
                              UC_ARM_REG_R3),inputs):uc.reg_write(reg,value)
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        uc.emu_start(start|1,0x300000,count=100)
        saved=uc.reg_read(UC_ARM_REG_R0)
        state=[int.from_bytes(uc.mem_read(context+i*4,4),'little')
               for i in range(8)]
        restore=(symbols['audio_uart_nema_stencil_restore_5226b2'] if compiled
                 else 0x5226b2)
        uc.reg_write(UC_ARM_REG_R0,saved)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        uc.emu_start(restore|1,0x300000,count=100)
        restored=[int.from_bytes(uc.mem_read(context+i*4,4),'little')
                  for i in range(8)]
        return saved,state,restored

    cases=0
    for bits in itertools.product((0,1),repeat=4):
        for previous in (0,0x07800000,0xffffffff):
            initial=[0,0,0,0x12345678,0x87654321,0xf0f00f0f,
                     0x55555555,previous]
            native=run(False,bits,initial)
            candidate=run(True,bits,initial)
            assert candidate==native,(bits,hex(previous),native,candidate)
            cases+=1
    print('PASS_NEMA_STENCIL_NATIVE',cases)
