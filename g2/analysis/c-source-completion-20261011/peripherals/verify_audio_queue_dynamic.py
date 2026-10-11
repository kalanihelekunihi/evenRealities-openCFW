#!/usr/bin/env python3
"""Valid-path stock/C FreeRTOS dynamic queue constructor comparison."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'g2/components/audio/queue_dynamic_source_candidate/create.c'
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    obj, path = directory / 'create.o', directory / 'create.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000',
                    '--defsym=pvPortMalloc=0x101011',
                    '--defsym=xQueueGenericReset=0x101021',
                    '--defsym=offline_assert=0x101031',
                    '-o', str(path), str(obj)], check=True, stderr=subprocess.DEVNULL)
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(item['p_vaddr'], item.data()) for item in elf.iter_segments() if item['p_type'] == 'PT_LOAD']
        symbols = {item.name: item['st_value'] for item in elf.get_section_by_name('.symtab').iter_symbols()}

    def run(native, count, size, kind, malloc_result):
        unit = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        unit.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        unit.mem_map(0x438000, (len(STOCK) + 4095) & ~4095)
        unit.mem_map(0x100000, 0x20000)
        unit.mem_map(0x20000000, 0x100000)
        unit.mem_write(0x438000, STOCK)
        if not native:
            for address, data in segments:
                unit.mem_write(address, data)
        unit.mem_write(0x20004000, bytes([0xa5]) * 80)
        for reg, value in ((A.UC_ARM_REG_R0, count), (A.UC_ARM_REG_R1, size),
                           (A.UC_ARM_REG_R2, kind), (A.UC_ARM_REG_SP, 0x200f0000),
                           (A.UC_ARM_REG_LR, 0x101181)):
            unit.reg_write(reg, value)
        targets = ({0x456110: 'malloc', 0x441516: 'reset'} if native else
                   {0x101010: 'malloc', 0x101020: 'reset'})
        calls = []
        done = [False]
        def hook(machine, pc, _size, _user):
            if pc == 0x101180:
                done[0] = True
                machine.emu_stop()
                return
            event = targets.get(pc)
            if event is None:
                return
            r0, r1 = machine.reg_read(A.UC_ARM_REG_R0), machine.reg_read(A.UC_ARM_REG_R1)
            calls.append((event, r0) if event == 'malloc' else (event, r0, r1))
            machine.reg_write(A.UC_ARM_REG_R0, malloc_result if event == 'malloc' else 1)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
        unit.hook_add(UC_HOOK_CODE, hook)
        unit.emu_start((0x441636 if native else symbols['audio_queue_create_dynamic']) | 1, 0, count=300)
        assert done[0], (native, count, size, kind, malloc_result)
        return (unit.reg_read(A.UC_ARM_REG_R0), calls,
                bytes(unit.mem_read(0x20004000, 80)))

    total = 0
    for count in (1, 3, 50):
        for size in (0, 1, 12):
            for kind in (0, 1, 2, 255):
                for malloc_result in (0, 0x20004000):
                    original = run(True, count, size, kind, malloc_result)
                    candidate = run(False, count, size, kind, malloc_result)
                    assert original == candidate, (count, size, kind, malloc_result,
                                                   original, candidate)
                    total += 1
    print('PASS_AUDIO_QUEUE_DYNAMIC', total)
