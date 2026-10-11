#!/usr/bin/env python3
"""Original-byte/C oracle for three I2S IRQ helpers."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as A

R = Path(__file__).resolve().parents[4]
D = Path(__file__).resolve().parent
S = R / 'g2/components/audio/codec_i2s_irq_candidate/irq.c'
O = D / 'codec-i2s-irq-m4.o'
E = D / 'codec-i2s-irq-oracle.elf'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(S), '-o', str(O)], check=True)
subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000', '-o', str(E), str(O)],
               check=True, stderr=subprocess.DEVNULL)
with E.open('rb') as fh:
    elf = ELFFile(fh)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']
    symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
stock = (R / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]

def run(original, name, irq=0, priority=0, prior=0):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(stock) + 4095) & ~4095)
    u.mem_map(0x100000, 0x20000)
    u.mem_map(0x20000000, 0x100000)
    u.mem_map(0xe000e000, 0x2000)
    if original:
        u.mem_write(0x438000, stock)
    else:
        for addr, data in segments:
            u.mem_write(addr, data)
    u.reg_write(A.UC_ARM_REG_R0, irq & 0xffffffff)
    u.reg_write(A.UC_ARM_REG_R1, priority)
    u.reg_write(A.UC_ARM_REG_SP, 0x200f0000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    u.reg_write(A.UC_ARM_REG_PRIMASK, prior)
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
    native = {'priority': 0x57a4b0, 'enable': 0x57a46c, 'global': 0x473934}
    source = {'priority': 'g2_codec_irq_priority',
              'enable': 'g2_codec_irq_enable',
              'global': 'g2_codec_global_irq_enable'}
    entry = native[name] if original else symbols[source[name]]
    u.emu_start(entry | 1, 0, count=80)
    assert done[0], (original, name, irq, priority, prior)
    result = (writes, u.reg_read(A.UC_ARM_REG_PRIMASK))
    if name == 'global':
        result += (u.reg_read(A.UC_ARM_REG_R0),)
    return result

cases = 0
for irq in (-16, -15, -1, 0, 1, 31, 32, 127, 255, 0x10001):
    for priority in (0, 4, 15, 255):
        for name in ('priority', 'enable'):
            a = run(True, name, irq, priority)
            b = run(False, name, irq, priority)
            assert a == b, (name, irq, priority, a, b)
            cases += 1
for prior in (0, 1):
    a = run(True, 'global', prior=prior)
    b = run(False, 'global', prior=prior)
    assert a == b == ([], 0, prior), (prior, a, b)
    cases += 1
print('PASS_AUDIO_CODEC_I2S_IRQ', cases)
