#!/usr/bin/env python3
"""Bounded stock/C comparison for the sensor cancel callback pointer store."""
from pathlib import Path
import subprocess, sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

H = Path(__file__).resolve().parent
R = H.parents[3]
subprocess.run([sys.executable, str(H / 'verify_case_sensor_irq_5f50.py')], check=True,
               stdout=subprocess.DEVNULL)
stock = (R / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
with (H / 'sensor_irq_5f50.oracle.elf').open('rb') as fp:
    elf = ELFFile(fp)
    sym = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD']

def run(native):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    uc.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    uc.mem_map(0x08000000, (len(stock) + 4095) & ~4095)
    uc.mem_write(0x08000000, stock)
    uc.mem_map(0x00100000, 0x10000)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_map(0x20000000, 0x10000)
    uc.mem_map(0x40010000, 0x1000)
    descriptor = 0x20000e24
    peripheral = 0x40010000
    child = 0x20002000
    uc.mem_write(descriptor, peripheral.to_bytes(4, 'little'))
    uc.mem_write(descriptor + 128, child.to_bytes(4, 'little'))
    uc.mem_write(peripheral, (0x100).to_bytes(4, 'little'))
    uc.mem_write(peripheral + 8, (0x40).to_bytes(4, 'little'))
    uc.mem_write(peripheral + 28, (1).to_bytes(4, 'little'))
    uc.reg_write(UC_ARM_REG_R0, descriptor)
    uc.reg_write(UC_ARM_REG_SP, 0x20007fc0)
    uc.reg_write(UC_ARM_REG_LR, 0x20008001)
    lower = ({0x080086f4: 'error', 0x080048e6: 'ready'} if native else
             {sym['case_boot_sensor_irq_error'] & ~1: 'error',
              sym['case_boot_sensor_irq_restart_ready'] & ~1: 'ready'})
    calls = []
    def hook(uc, address, size, unused):
        if address in lower:
            calls.append((lower[address], uc.reg_read(UC_ARM_REG_R0)))
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start((0x08005f50 if native else sym['case_irq_child_5f50']) | 1,
                 0x20008000, count=300)
    return calls, bytes(uc.mem_read(descriptor, 0xc0)), bytes(uc.mem_read(peripheral, 0x40)), \
        int.from_bytes(uc.mem_read(child + 56, 4), 'little')

native = run(True)
source = run(False)
assert native[:3] == source[:3], (native[:1], source[:1])
assert native[3] == 0x080086e1, hex(native[3])
assert source[3] == sym['case_boot_sensor_cancel_callback'] | 1, (hex(source[3]), hex(sym['case_boot_sensor_cancel_callback']))
print('PASS_CASE_SENSOR_IRQ_CALLBACK_RELOCATION 1')
