#!/usr/bin/env python3
"""Bounded original-byte/C MMIO oracle for the I2S start lower."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as A

R = Path(__file__).resolve().parents[4]
D = Path(__file__).resolve().parent
S = R / 'g2/components/audio/codec_i2s_start_candidate/start.c'
O = D / 'codec-i2s-start-m4.o'
E = D / 'codec-i2s-start-oracle.elf'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(S), '-o', str(O)], check=True)
subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000', '-o', str(E), str(O)],
               check=True, stderr=subprocess.DEVNULL)
with E.open('rb') as fh:
    elf = ELFFile(fh)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']
    symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
stock = (R / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]

def word(u, addr):
    return int.from_bytes(u.mem_read(addr, 4), 'little')

def putword(u, addr, value):
    u.mem_write(addr, (value & 0xffffffff).to_bytes(4, 'little'))

def run(original, mode, status, valid, tx, rx, channel):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(stock) + 4095) & ~4095)
    u.mem_map(0x100000, 0x20000)
    u.mem_map(0x20000000, 0x100000)
    u.mem_map(0x40208000, 0x3000)
    if original:
        u.mem_write(0x438000, stock)
    else:
        for addr, data in segments:
            u.mem_write(addr, data)
    handle = 0x20002000
    config = 0x20003000
    base = 0x40208000 + channel * 0x1000
    putword(u, handle, 0x01125125 if valid else 0xdeadbeef)
    putword(u, handle + 4, channel)
    putword(u, handle + 0x10 * 4, tx)
    putword(u, handle + 0x12 * 4, rx)
    putword(u, handle + 0x15 * 4, 0x1234)
    putword(u, handle + 0x16 * 4, 0x5678)
    putword(u, base + 0x28, status)
    putword(u, base + 0x200, 0x80)
    u.mem_write(config + 1, bytes([mode]))
    u.reg_write(A.UC_ARM_REG_R0, handle)
    u.reg_write(A.UC_ARM_REG_R1, config)
    u.reg_write(A.UC_ARM_REG_SP, 0x200f0000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    writes = []
    done = [False]
    def written(cpu, _access, addr, size, value, _user):
        writes.append((addr, size, value & ((1 << (size * 8)) - 1)))
    def stop(cpu, pc, _size, _user):
        if pc == 0x101180:
            done[0] = True
            cpu.emu_stop()
    u.hook_add(UC_HOOK_MEM_WRITE, written)
    u.hook_add(UC_HOOK_CODE, stop)
    u.emu_start((0x5904ce if original else symbols['g2_codec_i2s_start']) | 1,
                0, count=500)
    assert done[0], (original, mode, status, valid, tx, rx, channel)
    mmio = [x for x in writes if 0x40208000 <= x[0] < 0x4020b000]
    ram = [x for x in writes if 0x20002000 <= x[0] < 0x20002100]
    return u.reg_read(A.UC_ARM_REG_R0), mmio, ram, bytes(u.mem_read(handle, 0x60))

cases = 0
for mode in (0, 1, 2, 3):
    for status in (0, 1, 0x10000000, 0x20000000):
        for valid in (False, True):
            for tx, rx in ((0x9000, 0xa000), (0xffffffff, 0xa000),
                           (0x9000, 0xffffffff)):
                for channel in (0, 1):
                    a = run(True, mode, status, valid, tx, rx, channel)
                    b = run(False, mode, status, valid, tx, rx, channel)
                    assert a == b, (mode, status, valid, tx, rx, channel, a, b)
                    cases += 1
print('PASS_AUDIO_CODEC_I2S_START', cases)
