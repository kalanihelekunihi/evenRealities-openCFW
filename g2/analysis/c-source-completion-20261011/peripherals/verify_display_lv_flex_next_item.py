"""Compare compiled C with native 0x48c770 over bounded index/direction cases."""
from pathlib import Path
import struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *

ROOT = Path(__file__).resolve().parents[3]
BLOB = (ROOT / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC = ROOT / 'components/audio/uart_thread_source_candidate/display_lv_flex_next_item.c'
with tempfile.TemporaryDirectory() as td:
    elf = Path(td) / 'test.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-O2', '-Wall', '-Wextra', '-Werror', '-nostdlib', '-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_uart_lv_flex_next_item_48c770', str(SRC), '-o', str(elf)], check=True)
    syms = {v[2]: int(v[0], 16) for line in subprocess.check_output(
        ['arm-none-eabi-nm', str(elf)], text=True).splitlines() if len(v := line.split()) == 3}
    with elf.open('rb') as f:
        segs = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments() if s['p_type'] == 'PT_LOAD']
    cases = 0
    for reverse in (0, 1, 0x100, 0x101):
        for index in (-1, 0, 1, 2, 3):
            out = []
            for is_c in (False, True):
                u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
                u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, BLOB)
                u.mem_map(0x100000, 0x100000); u.mem_map(0x20000000, 0x100000)
                for a, d in segs: u.mem_write(a, d)
                obj, spec, children, cell = 0x20003000, 0x20003100, 0x20003200, 0x20003300
                u.mem_write(obj + 8, struct.pack('<I', spec))
                u.mem_write(spec, struct.pack('<I', children))
                u.mem_write(spec + 0x30, struct.pack('<H', 3))
                u.mem_write(children, struct.pack('<III', 0x20004000, 0x20004020, 0x20004040))
                u.mem_write(cell, struct.pack('<i', index))
                u.reg_write(UC_ARM_REG_SP, 0x200ff000); u.reg_write(UC_ARM_REG_LR, 0x600001)
                u.reg_write(UC_ARM_REG_R0, obj); u.reg_write(UC_ARM_REG_R1, reverse)
                u.reg_write(UC_ARM_REG_R2, cell)
                u.emu_start((syms['audio_uart_lv_flex_next_item_48c770'] if is_c else 0x48c770) | 1,
                            0x600000, count=80)
                out.append((u.reg_read(UC_ARM_REG_R0), bytes(u.mem_read(cell, 4))))
            assert out[0] == out[1], (reverse, index, out)
            cases += 1
    print(f'PASS {cases} compiled-C/native LV flex next-item cases')
