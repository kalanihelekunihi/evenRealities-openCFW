#!/usr/bin/env python3
"""Stock/C oracle for the full private PCM unregistration body."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

R = Path(__file__).resolve().parents[4]
D = Path(__file__).resolve().parent
S = R / 'g2/components/audio/pcm_unregister_source_candidate/unregister.c'
O = D / 'pcm-unregister-m4.o'
E = D / 'pcm-unregister-oracle.elf'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(S), '-o', str(O)], check=True)
subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000',
                '--defsym=g2_pcm_registration_rows=0x20073c20',
                '--defsym=audio_log_flags=0x101011',
                '--defsym=audio_log_extended=0x101021',
                '--defsym=audio_log_simple=0x101031',
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

def run(original, app, index, slot, flags):
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
    addr = 0x20073c20 + (index & 255) * 12
    for i, value in enumerate(slot):
        putword(u, addr + i * 4, value)
    u.reg_write(A.UC_ARM_REG_R0, app)
    u.reg_write(A.UC_ARM_REG_R1, index)
    u.reg_write(A.UC_ARM_REG_SP, 0x200f0000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    calls = ({0x43d0ce: 'flags', 0x43d574: 'extended',
              0x43ce9e: 'simple'} if original else
             {0x101010: 'flags', 0x101020: 'extended', 0x101030: 'simple'})
    events = []
    read_count = [0]
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
        if kind == 'flags':
            events.append((kind,))
            result = flags[read_count[0] % len(flags)]
            read_count[0] += 1
        elif kind == 'extended':
            line = word(cpu, sp)
            fmt = cstr(cpu, word(cpu, sp + 4))
            args = ((word(cpu, sp + 8), word(cpu, sp + 12)) if line == 221
                    else (word(cpu, sp + 8),) if line == 225 else ())
            events.append((kind, r0, cstr(cpu, r1), cstr(cpu, r2),
                           cstr(cpu, r3), line, fmt, args))
            result = 0
        else:
            fmt = cstr(cpu, r1)
            args = ((r3, word(cpu, sp)) if 'not found' in fmt else
                    (r3,) if 'unregistered' in fmt else ())
            events.append((kind, r0, fmt, cstr(cpu, r2), args))
            result = 0
        cpu.reg_write(A.UC_ARM_REG_R0, result)
        cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE, hook)
    u.emu_start((0x57acd0 if original else symbols['audio_unregister']) | 1,
                0, count=400)
    assert done[0], (original, app, index, slot, flags)
    return u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(addr, 12)), events

cases = 0
for app in (0, 7, 10):
    for index in (0, 1, 255, 0x101):
        for slot in ((0, 0, 0), (7, 5, 1), (10, 9, 2)):
            for flags in ((0,), (1,), (2,), (4,), (7,), (0, 4, 0)):
                a = run(True, app, index, slot, flags)
                b = run(False, app, index, slot, flags)
                assert a == b, (app, index, slot, flags, a, b)
                cases += 1
print('PASS_AUDIO_PCM_UNREGISTER', cases)
