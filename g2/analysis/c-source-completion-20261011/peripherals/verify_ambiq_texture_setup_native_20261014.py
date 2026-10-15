#!/usr/bin/env python3
"""Compare Ambiq texture mode cache and lower-call decisions."""
from pathlib import Path
import random
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP,
                               UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,
                               UC_ARM_REG_R3)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/texture_setup.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=(('audio_uart_ambiq_default_unit_4c791a',0x4c791a),
       ('display_driver_nema_mode_513924',0x513924))
with tempfile.TemporaryDirectory() as temp:
    stub=Path(temp)/'lower.c'
    stub.write_text('unsigned audio_uart_ambiq_default_unit_4c791a(void)'
                    '{return 0;}\nvoid display_driver_nema_mode_513924('
                    'unsigned a,unsigned b,unsigned c,unsigned d){}\n')
    image=Path(temp)/'setup.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4',
                    '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),
                    str(stub),'-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in
                 elf.get_section_by_name('.symtab').iter_symbols()}
    regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
    def run(compiled,inputs,initial):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        unit=0x20008000;stack=0x200f0000
        uc.mem_write(unit,initial)
        trace=[]
        def hook(emu,address,size,user):
            for name,native in lower:
                target=(symbols[name]&~1) if compiled else native
                if address!=target:continue
                if name==lower[0][0]:
                    trace.append(('default',))
                    emu.reg_write(UC_ARM_REG_R0,unit)
                else:
                    trace.append(('mode',tuple(emu.reg_read(r) for r in regs)))
                emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
                return
        uc.hook_add(UC_HOOK_CODE,hook)
        for reg,value in zip(regs,inputs[:4]):uc.reg_write(reg,value&0xffffffff)
        uc.mem_write(stack,(inputs[4]&0xffffffff).to_bytes(4,'little')+
                     (inputs[5]&0xffffffff).to_bytes(4,'little'))
        uc.reg_write(UC_ARM_REG_SP,stack)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        start=(symbols['audio_uart_ambiq_texture_setup_4b06c0'] if compiled
               else 0x4b06c0)
        uc.emu_start(start|1,0x300000,count=130)
        return bytes(uc.mem_read(unit,128)),trace
    rng=random.Random(0x4b06c0)
    cases=[]
    for unit in (0,0x20008000):
        for mode in (0,6,0x12345678):
            for flags in ((3,2,8,0),(3,2,8,1),(255,128,254,0),
                          (0,0,0,0x100),(0,0,0,0x101)):
                cases.append((unit,mode,*flags))
    cases += [(rng.choice((0,0x20008000)),rng.getrandbits(32),
               rng.getrandbits(32),rng.getrandbits(32),
               rng.getrandbits(32),rng.getrandbits(32)) for _ in range(128)]
    count=0
    for inputs in cases:
        for matched in (False,True):
            initial=bytearray(rng.randbytes(128))
            if matched:
                initial[0x50:0x54]=(inputs[1]&0xffffffff).to_bytes(4,'little')
                initial[0x54:0x57]=bytes(v&0xff for v in inputs[2:5])
            native=run(False,inputs,bytes(initial))
            candidate=run(True,inputs,bytes(initial))
            assert candidate==native,(inputs,matched,native,candidate)
            count+=1
    print('PASS_AMBIQ_TEXTURE_SETUP_NATIVE',count)
