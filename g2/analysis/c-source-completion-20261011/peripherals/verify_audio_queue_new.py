#!/usr/bin/env python3
"""Controlled stock/C CMSIS osMessageQueueNew constructor comparison."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'g2/components/audio/audio_queue_new_source_candidate/new.c'
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]

with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    obj, path = directory / 'new.o', directory / 'new.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    definitions = {'audio_irq_context': 0x101011,
                   'audio_queue_create_static': 0x101021,
                   'audio_queue_create_dynamic': 0x101031}
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000',
                    *[f'--defsym={key}=0x{value:x}' for key, value in definitions.items()],
                    '-o', str(path), str(obj)], check=True, stderr=subprocess.DEVNULL)
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(item['p_vaddr'], item.data()) for item in elf.iter_segments() if item['p_type'] == 'PT_LOAD']
        symbols = {item.name: item['st_value'] for item in elf.get_section_by_name('.symtab').iter_symbols()}

    def run(native, count, size, context, kind):
        unit = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        unit.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        unit.mem_map(0x438000, (len(STOCK) + 4095) & ~4095)
        unit.mem_map(0x100000, 0x20000)
        unit.mem_map(0x20000000, 0x100000)
        unit.mem_write(0x438000, STOCK)
        if not native:
            for address, data in segments:
                unit.mem_write(address, data)
        attribute = 0 if kind == 0 else 0x20001000
        fields = {1: (0, 0, 0, 0), 2: (0x20002000, 80, 0x20003000, count*size),
                  3: (0x20002000, 79, 0x20003000, count*size),
                  4: (0x20002000, 80, 0x20003000, max(0, count*size-1)),
                  5: (0x20002000, 0, 0, 0)}
        if attribute:
            for offset, value in zip((8, 12, 16, 20), fields[kind]):
                unit.mem_write(attribute+offset, (value & 0xffffffff).to_bytes(4, 'little'))
        for reg, value in ((A.UC_ARM_REG_R0, count), (A.UC_ARM_REG_R1, size),
                           (A.UC_ARM_REG_R2, attribute), (A.UC_ARM_REG_SP, 0x200f0000),
                           (A.UC_ARM_REG_LR, 0x101181)):
            unit.reg_write(reg, value)
        targets = ({0x44900e: 'context', 0x4415ca: 'static', 0x441636: 'dynamic'}
                   if native else {0x101010: 'context', 0x101020: 'static', 0x101030: 'dynamic'})
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
            args = tuple(machine.reg_read(getattr(A, f'UC_ARM_REG_R{i}')) for i in range(4))
            if event == 'context':
                calls.append((event,))
                machine.reg_write(A.UC_ARM_REG_R0, context)
            else:
                fifth = int.from_bytes(machine.mem_read(machine.reg_read(A.UC_ARM_REG_SP), 4), 'little') if event == 'static' else None
                calls.append((event, *args[:5 if event == 'static' else 3], fifth))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20004000 if event == 'static' else 0x20005000)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
        unit.hook_add(UC_HOOK_CODE, hook)
        entry = 0x449a32 if native else symbols['audio_queue_new']
        unit.emu_start(entry | 1, 0, count=250)
        assert done[0], (native, count, size, context, kind)
        return unit.reg_read(A.UC_ARM_REG_R0), calls

    total = 0
    for count in (0, 1, 3, 50):
        for size in (0, 1, 12):
            for context in (0, 1):
                for kind in range(6):
                    original = run(True, count, size, context, kind)
                    candidate = run(False, count, size, context, kind)
                    assert original == candidate, (count, size, context, kind, original, candidate)
                    total += 1
    print('PASS_AUDIO_QUEUE_NEW', total)
