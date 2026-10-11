#!/usr/bin/env python3
"""Bounded stock/C call-order oracle for DRV_Gx8002_I2SInit."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

R = Path(__file__).resolve().parents[4]
D = Path(__file__).resolve().parent
S = R / 'g2/components/audio/codec_i2s_init_source_candidate/init.c'
O = D / 'codec-i2s-init-m4.o'
E = D / 'codec-i2s-init-oracle.elf'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(S), '-o', str(O)], check=True)
children = [
    ('g2_codec_clock_enable', 0x4c3074, 'clock', 2),
    ('g2_codec_i2s_acquire', 0x59005e, 'acquire', 2),
    ('g2_codec_i2s_disable', 0x590648, 'disable', 3),
    ('g2_codec_i2s_configure', 0x590104, 'configure', 2),
    ('g2_codec_i2s_prepare', 0x590b92, 'prepare', 1),
    ('g2_codec_i2s_dma_configure', 0x590a24, 'dma', 3),
    ('g2_codec_irq_priority', 0x57a4b0, 'priority', 2),
    ('g2_codec_irq_enable', 0x57a46c, 'irq_enable', 1),
    ('g2_codec_global_irq_enable', 0x473934, 'global_irq', 0),
    ('g2_codec_i2s_start', 0x5904ce, 'start', 2),
    ('audio_log_flags', 0x43d0ce, 'flags', 0),
    ('audio_log_extended', 0x43d574, 'extended', 0),
    ('audio_log_simple', 0x43ce9e, 'simple', 0),
]
data = {'g2_codec_i2s_initialized': 0x20074fb7,
        'g2_codec_i2s_handle': 0x2007450c,
        'g2_codec_i2s_config_base': 0x20000000,
        'g2_codec_i2s_dma_descriptor': 0x20000740,
        'g2_codec_i2s_irq_number': 0x78f558}
source_calls = {0x101000 + 0x10 * i: (kind, argc)
                for i, (_name, _addr, kind, argc) in enumerate(children)}
stock_calls = {addr: (kind, argc) for _name, addr, kind, argc in children}
subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000',
                *[f'--defsym={name}={addr:#x}' for name, addr in data.items()],
                *[f'--defsym={name}={addr+1:#x}'
                  for addr, (name, _native, _kind, _argc) in
                  zip(source_calls, children)],
                '-o', str(E), str(O)], check=True, stderr=subprocess.DEVNULL)
with E.open('rb') as fh:
    elf = ELFFile(fh)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']
    symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
stock = (R / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]

def word(u, addr):
    return int.from_bytes(u.mem_read(addr, 4), 'little')

def putword(u, addr, value):
    u.mem_write(addr, (value & 0xffffffff).to_bytes(4, 'little'))

def cstr(u, addr):
    return bytes(u.mem_read(addr, 256)).split(b'\0', 1)[0].decode('ascii')

def run(original, initial, flags):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(stock) + 4095) & ~4095)
    u.mem_map(0x100000, 0x20000)
    u.mem_map(0x20000000, 0x100000)
    u.mem_write(0x438000, stock)
    if not original:
        for addr, segment in segments:
            u.mem_write(addr, segment)
    u.mem_write(0x20074fb7, bytes([initial]))
    putword(u, 0x2007450c, 0)
    u.reg_write(A.UC_ARM_REG_SP, 0x200f0000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    events = []
    reads = [0]
    done = [False]
    calls = stock_calls if original else source_calls
    def hook(cpu, pc, _size, _user):
        if pc == 0x101180:
            done[0] = True
            cpu.emu_stop()
            return
        item = calls.get(pc)
        if item is None:
            return
        kind, argc = item
        args = [cpu.reg_read(reg) for reg in (A.UC_ARM_REG_R0,
                A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
        sp = cpu.reg_read(A.UC_ARM_REG_SP)
        if kind == 'flags':
            events.append((kind,))
            result = flags[reads[0] % len(flags)]
            reads[0] += 1
        elif kind == 'extended':
            events.append((kind, args[0], cstr(cpu, args[1]), cstr(cpu, args[2]),
                           cstr(cpu, args[3]), word(cpu, sp), cstr(cpu, word(cpu, sp + 4))))
            result = 0
        elif kind == 'simple':
            events.append((kind, args[0], cstr(cpu, args[1]), cstr(cpu, args[2])))
            result = 0
        else:
            events.append((kind, *args[:argc]))
            if kind == 'acquire':
                putword(cpu, args[1], 0x20001000)
            result = 0
        cpu.reg_write(A.UC_ARM_REG_R0, result)
        cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE, hook)
    u.emu_start((0x57a65c if original else symbols['audio_i2s_enable']) | 1,
                0, count=500)
    assert done[0], (original, initial, flags)
    return bytes(u.mem_read(0x20074fb7, 1)), word(u, 0x2007450c), events

cases = 0
for initial in (0, 1, 2):
    for flags in ((0,), (1,), (2,), (4,), (7,), (0, 4, 0), (2, 0, 4)):
        a = run(True, initial, flags)
        b = run(False, initial, flags)
        assert a == b, (initial, flags, a, b)
        cases += 1
print('PASS_AUDIO_CODEC_I2S_INIT', cases)
