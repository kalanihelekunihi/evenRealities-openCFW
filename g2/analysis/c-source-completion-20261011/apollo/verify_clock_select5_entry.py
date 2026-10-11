#!/usr/bin/env python3
"""Bounded stock/C class-5 clock config entry comparison at 0x4217d2."""
from pathlib import Path
import subprocess, struct, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
SOURCE = ROOT / 'g2/components/bootloader/initializer_callbacks/startup_clock_config.c'
with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    obj = temp / 'clock.o'
    subprocess.run(['/usr/bin/clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
                    '-mthumb', '-mfpu=fpv5-sp-d16', '-mfloat-abi=softfp', '-O2',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE), '-o', str(obj)],
                   check=True)
    undefined = subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-nm', '-u', str(obj)], text=True)
    names = [line.split()[-1] for line in undefined.splitlines() if line.strip()]
    stub = temp / 'stub.S'
    stub.write_text('.syntax unified\n.thumb\n.text\n' + ''.join(
        f'.global {name}\n.thumb_func\n{name}:\nbx lr\n' for name in names))
    stubobj = temp / 'stub.o'
    subprocess.run(['/usr/bin/clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
                    '-mthumb', '-c', str(stub), '-o', str(stubobj)], check=True)
    elfpath = temp / 'clock.elf'
    subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld', '-Ttext=0x00500000',
                    str(obj), str(stubobj), '-o', str(elfpath)], check=True,
                   stderr=subprocess.DEVNULL)
    with elfpath.open('rb') as stream:
        image = ELFFile(stream)
        symbols = {s.name: s['st_value'] for s in image.get_section_by_name('.symtab').iter_symbols()}
        segments = [(p['p_vaddr'], p.data()) for p in image.iter_segments() if p['p_type'] == 'PT_LOAD']
    cases = [
        ('invalid', 123, None, 0, 0),
        ('missing-ref-auto', 196608000, None, 0, 0),
        ('missing-ref-mode0', 250000000, bytes((0,))*12, 0, 0),
        ('missing-ref-mode1', 250000000, bytes((1,))*12, 0, 0),
        ('disable-idle', 0, None, 0, 0),
        ('enable-mode0', 250000000, bytes((0,2,0,0,0xba,0x49,0x0c,0,0,0,0,0)), 24000000, 0),
        ('enable-mode1', 196608000, bytes((1,2,0,0,0xba,0x49,0x0c,0,0,0,0,0)), 0, 24000000),
    ]
    for label, rate, config, ref0, ref1 in cases:
        pair = []
        for native in (True, False):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            u.mem_map(0x00410000, 0x40000)
            u.mem_write(0x00410000, STOCK)
            u.mem_map(0x00500000, 0x10000)
            if not native:
                for address, data in segments:
                    u.mem_write(address, data)
            u.mem_map(0x20000000, 0x30000)
            u.mem_map(0x40000000, 0x10000)
            u.mem_write(0x20000080, struct.pack('<I', ref0))
            u.mem_write(0x2000008c, struct.pack('<I', ref1))
            if config is not None:
                u.mem_write(0x20010000, config)
            u.reg_write(UC_ARM_REG_R0, rate)
            u.reg_write(UC_ARM_REG_R1, 0 if config is None else 0x20010000)
            u.reg_write(UC_ARM_REG_SP, 0x2002f000)
            u.reg_write(UC_ARM_REG_LR, 0x0050f001)
            entry = 0x004217d2 if native else symbols['opencfw_boot_startup_select5'] & ~1
            try:
                u.emu_start(entry | 1, 0x0050f000, count=10000)
            except Exception as exc:
                raise AssertionError((label, native, hex(u.reg_read(UC_ARM_REG_PC)))) from exc
            pair.append((u.reg_read(UC_ARM_REG_R0), u.reg_read(UC_ARM_REG_PRIMASK),
                         bytes(u.mem_read(0x20026ff8, 12)),
                         bytes(u.mem_read(0x20027034, 4)),
                         bytes(u.mem_read(0x20000551, 1))))
        assert pair[0] == pair[1], (label, pair)
    print('PASS_BOOT_CLOCK_SELECT5_ENTRY', len(cases))
