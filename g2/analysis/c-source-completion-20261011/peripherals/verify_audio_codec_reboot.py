#!/usr/bin/env python3
"""Original-byte/compiled-C callback oracle for DRV_Gx8002_Reboot."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

R = Path(__file__).resolve().parents[4]
D = Path(__file__).resolve().parent
S = R / 'g2/components/audio/codec_reboot_source_candidate/reboot.c'
O = D / 'codec-reboot-m4.o'
E = D / 'codec-reboot-oracle.elf'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(S), '-o', str(O)], check=True)
names = ['g2_codec_power_off', 'audio_delay', 'g2_codec_power_on',
         'audio_log_flags', 'audio_log_extended', 'audio_log_simple']
addresses = {name: 0x101000 + 0x10 * i for i, name in enumerate(names)}
subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000',
                *[f'--defsym={name}={addr+1:#x}' for name, addr in addresses.items()],
                '-o', str(E), str(O)], check=True, stderr=subprocess.DEVNULL)
with E.open('rb') as fh:
    elf = ELFFile(fh)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']
    symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
stock = (R / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]

def word(u, addr):
    return int.from_bytes(u.mem_read(addr, 4), 'little')

def cstr(u, addr):
    return bytes(u.mem_read(addr, 256)).split(b'\0', 1)[0].decode('ascii')

def run(original, mode, flags):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(stock) + 4095) & ~4095)
    u.mem_map(0x100000, 0x20000)
    u.mem_map(0x20000000, 0x100000)
    if original:
        u.mem_write(0x438000, stock)
    else:
        for addr, data in segments:
            u.mem_write(addr, data)
    u.reg_write(A.UC_ARM_REG_R0, mode)
    u.reg_write(A.UC_ARM_REG_SP, 0x200f0000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    calls = ({0x57a5bc: 'off', 0x449376: 'delay', 0x57a508: 'on',
              0x43d0ce: 'flags', 0x43d574: 'extended', 0x43ce9e: 'simple'}
             if original else dict(zip(addresses.values(),
                 ('off', 'delay', 'on', 'flags', 'extended', 'simple'))))
    events = []
    flag_reads = [0]
    done = [False]

    def hook(cpu, pc, _size, _user):
        if pc == 0x101180:
            done[0] = True
            cpu.emu_stop()
            return
        kind = calls.get(pc)
        if kind is None:
            return
        r0 = cpu.reg_read(A.UC_ARM_REG_R0)
        r1 = cpu.reg_read(A.UC_ARM_REG_R1)
        r2 = cpu.reg_read(A.UC_ARM_REG_R2)
        r3 = cpu.reg_read(A.UC_ARM_REG_R3)
        sp = cpu.reg_read(A.UC_ARM_REG_SP)
        if kind == 'delay':
            events.append((kind, r0))
            result = 0
        elif kind == 'flags':
            events.append((kind,))
            result = flags[flag_reads[0] % len(flags)]
            flag_reads[0] += 1
        elif kind == 'extended':
            events.append((kind, r0, cstr(cpu, r1), cstr(cpu, r2),
                           cstr(cpu, r3), word(cpu, sp), cstr(cpu, word(cpu, sp + 4))))
            result = 0
        elif kind == 'simple':
            events.append((kind, r0, cstr(cpu, r1), cstr(cpu, r2)))
            result = 0
        else:
            events.append((kind,))
            result = 0
        cpu.reg_write(A.UC_ARM_REG_R0, result)
        cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

    u.hook_add(UC_HOOK_CODE, hook)
    u.emu_start((0x57a816 if original else symbols['audio_special_control']) | 1,
                0, count=300)
    assert done[0], (original, mode, flags)
    return events

cases = 0
for mode in (0, 1, 2, 0x100, 0x101, 0xffffffff):
    for flags in ((0,), (1,), (2,), (4,), (7,), (0, 4, 0), (2, 0, 4)):
        a = run(True, mode, flags)
        b = run(False, mode, flags)
        assert a == b, (mode, flags, a, b)
        cases += 1
print('PASS_AUDIO_CODEC_REBOOT', cases)
