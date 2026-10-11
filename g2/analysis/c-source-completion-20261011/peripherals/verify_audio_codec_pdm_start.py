#!/usr/bin/env python3
"""Bounded native-byte versus compiled C PDM descriptor/start transitions."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as A

R = Path(__file__).resolve().parents[4]
S = R / 'g2/components/audio/codec_pdm_start_source_candidate/start.c'
STOCK = (R / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
    obj = Path(tmp) / 'start.o'
    elf = Path(tmp) / 'start.elf'
    shim = Path(tmp) / 'shim.c'
    shim.write_text('#include <stdint.h>\nvoid stock_delay_us(uint32_t us) {(void)us;}\n')
    so = Path(tmp) / 'shim.o'
    flags = ['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb', '-O2', '-Wall', '-Wextra', '-Werror']
    subprocess.run(flags + ['-c', str(S), '-o', str(obj)], check=True)
    subprocess.run(flags + ['-c', str(shim), '-o', str(so)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000', '-o', str(elf), str(obj), str(so)], check=True)
    with elf.open('rb') as f:
        e = ELFFile(f)
        segs = [(p['p_vaddr'], p.data()) for p in e.iter_segments() if p['p_type'] == 'PT_LOAD']
        sym = {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}

    def put(u, address, word):
        u.mem_write(address, (word & 0xffffffff).to_bytes(4, 'little'))

    def run(native, valid, size, second, clear, instance):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x438000, (len(STOCK)+4095)&~4095)
        u.mem_map(0x100000, 0x20000)
        u.mem_map(0x20000000, 0x100000)
        u.mem_map(0x40201000, 0x5000)
        if native:
            u.mem_write(0x438000, STOCK)
        else:
            for base, data in segs:
                u.mem_write(base, data)
        h, d = 0x20002000, 0x20003000
        for offset, value in [(0, 0x01f956e2 if valid else 0), (8, instance), (12, 99), (16, 98), (20, 97), (24, 96)]:
            put(u, h+offset, value)
        for offset, value in [(0, 0x20009000), (4, second), (8, size)]:
            put(u, d+offset, value)
        reg = 0x40201000 + (instance << 12)
        put(u, reg+0x140, 0xa0)
        put(u, reg+0x148, 0x2200)
        u.reg_write(A.UC_ARM_REG_R0, h)
        u.reg_write(A.UC_ARM_REG_R1, d)
        u.reg_write(A.UC_ARM_REG_SP, 0x200f0000)
        u.reg_write(A.UC_ARM_REG_LR, 0x101181)
        writes, delays, done = [], [], [False]
        delay_pc = 0x4807a0 if native else sym['stock_delay_us'] & ~1
        def code(c, pc, _sz, _data):
            if pc == 0x101180:
                done[0] = True
                c.emu_stop()
            elif pc == delay_pc:
                delays.append(c.reg_read(A.UC_ARM_REG_R0))
                if clear:
                    put(c, reg+0x168, 0)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
        def write(_c, _access, address, width, value, _data):
            if 0x40201000 <= address < 0x40206000:
                writes.append((address, width, value & ((1 << (8*width))-1)))
        u.hook_add(UC_HOOK_CODE, code)
        u.hook_add(UC_HOOK_MEM_WRITE, write)
        u.emu_start((0x59235e if native else sym['g2_pdm_start']) | 1, 0, count=400)
        assert done[0]
        return (u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(h, 32)), writes, delays)

    cases = 0
    for valid in (False, True):
        for size in (0, 16, 20, 24, 48, 60, 64, 72, 77):
            for second in (0xffffffff, 0x2000a000):
                for clear in (False, True):
                    for instance in (0, 1):
                        native = run(True, valid, size, second, clear, instance)
                        source = run(False, valid, size, second, clear, instance)
                        assert native == source, (valid, size, second, clear, instance, native, source)
                        cases += 1
    print('PASS_AUDIO_CODEC_PDM_START', cases)
