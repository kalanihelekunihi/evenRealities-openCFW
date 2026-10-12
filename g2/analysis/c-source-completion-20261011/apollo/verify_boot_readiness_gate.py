#!/usr/bin/env python3
"""Bounded native/source ABI oracle for hardware readiness gate 0x42bf54."""
from pathlib import Path
import hashlib
import itertools
import struct
import subprocess
import tempfile

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

root = Path(__file__).resolve().parents[4]
stock = (root / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'

with tempfile.TemporaryDirectory() as folder:
    work = Path(folder)
    source = root / 'g2/components/bootloader/initializer_callbacks/hardware_readiness_gate.S'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-c', str(source), '-o', str(work / 'gate.o')], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x10000', '-e',
                    'opencfw_boot_hardware_readiness_gate',
                    '--defsym=opencfw_bl_mspi_mode_enter=0x11001',
                    '--defsym=opencfw_boot_startup_temperature=0x11101',
                    '--defsym=opencfw_boot_control_delay_status_change=0x11201',
                    str(work / 'gate.o'), '-o', str(work / 'gate.elf')],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary',
                    str(work / 'gate.elf'), str(work / 'gate.bin')], check=True)
    source_code = (work / 'gate.bin').read_bytes()
    child_maps = ({0x41bf84: 'enter', 0x41ca2c: 'temperature', 0x41d21c: 'poll'},
                  {0x11000: 'enter', 0x11100: 'temperature', 0x11200: 'poll'})

    def run(original, flag_a, flag_b, enter, temperature, poll):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x10000, 0x3000)
        cpu.mem_map(0x410000, 0x25000)
        cpu.mem_map(0x20000000, 0x3000)
        cpu.mem_map(0x40000000, 0x30000)
        cpu.mem_write(0x10000, source_code)
        cpu.mem_write(0x410000, stock)
        cpu.mem_write(0x40021008, struct.pack('<I', flag_a))
        cpu.mem_write(0x40021010, struct.pack('<I', flag_b))
        cpu.reg_write(a.UC_ARM_REG_SP, 0x20002000)
        cpu.reg_write(a.UC_ARM_REG_LR, 0x20001001)
        for reg, value in ((a.UC_ARM_REG_R5, 0x12345678),
                           (a.UC_ARM_REG_R6, 0x98765432),
                           (a.UC_ARM_REG_R7, 0xcafebabe)):
            cpu.reg_write(reg, value)
        events = []
        done = []
        children = child_maps[0 if original else 1]
        def hook(machine, pc, size, unused):
            if pc == 0x20001000:
                done.append(True)
                machine.emu_stop()
            if pc in children:
                name = children[pc]
                events.append((name, tuple(machine.reg_read(reg) for reg in
                              (a.UC_ARM_REG_R0, a.UC_ARM_REG_R1,
                               a.UC_ARM_REG_R2, a.UC_ARM_REG_R3)),
                               machine.reg_read(a.UC_ARM_REG_SP),
                               machine.reg_read(a.UC_ARM_REG_S0)))
                machine.reg_write(a.UC_ARM_REG_R0,
                                  {'enter': enter, 'temperature': temperature,
                                   'poll': poll}[name])
                machine.reg_write(a.UC_ARM_REG_PC, machine.reg_read(a.UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x42bf54 if original else 0x10000) | 1,
                      0x20001002, count=1000)
        assert done
        return (cpu.reg_read(a.UC_ARM_REG_R0), cpu.reg_read(a.UC_ARM_REG_R1),
                cpu.reg_read(a.UC_ARM_REG_SP), events)

    count = 0
    for args in itertools.product((0, 1), (0, 1), (0, 5), (0, 7), (0, 3)):
        native = run(True, *args)
        selected = run(False, *args)
        assert native[:3] == selected[:3], (args, native, selected)
        assert [e[0] for e in native[3]] == [e[0] for e in selected[3]], (args, native, selected)
        for n, s in zip(native[3], selected[3]):
            assert n[1][0] == s[1][0], (args, native, selected)
            if n[0] == 'temperature':
                assert n[3] == s[3] == 0xc2200000, (args, native, selected)
                assert n[2] == s[2], (args, native, selected)
            if n[0] == 'poll':
                assert n[1] == s[1] == (2500, 0x400083e0, 1, 0), (args, native, selected)
        count += 1
    print('PASS native/source readiness gate', count, 'branch cases')
