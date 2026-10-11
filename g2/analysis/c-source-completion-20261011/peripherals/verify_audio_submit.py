#!/usr/bin/env python3
"""Bounded original-byte/C comparison for AUD_SendMessage (0x53c638)."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'g2/components/audio/audio_submit_source_candidate/submit.c'
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]

with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    obj, elf_path = directory / 'submit.o', directory / 'submit.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    definitions = {'g2_audio_dispatch_state': 0x20003f98,
                   'audio_cmsis_queue_put': 0x101011,
                   'audio_flags_set': 0x101021,
                   'audio_log_flags': 0x101031,
                   'audio_log_extended': 0x101041,
                   'audio_log_simple': 0x101051}
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000',
                    *[f'--defsym={key}=0x{value:x}' for key, value in definitions.items()],
                    '-o', str(elf_path), str(obj)], check=True, stderr=subprocess.DEVNULL)
    with elf_path.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(item['p_vaddr'], item.data()) for item in elf.iter_segments() if item['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}

    def run(native, message, queue, status, flags):
        machine = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        machine.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        machine.mem_map(0x438000, (len(STOCK) + 4095) & ~4095)
        machine.mem_map(0x100000, 0x20000)
        machine.mem_map(0x20000000, 0x100000)
        machine.mem_write(0x438000, STOCK)
        if not native:
            for address, data in segments:
                machine.mem_write(address, data)
        machine.mem_write(0x20003fa4, queue.to_bytes(4, 'little'))
        machine.mem_write(0x20003fa0, (0x20008000).to_bytes(4, 'little'))
        machine.reg_write(A.UC_ARM_REG_R0, message)
        machine.reg_write(A.UC_ARM_REG_SP, 0x200f0000)
        machine.reg_write(A.UC_ARM_REG_LR, 0x101181)
        targets = ({0x449abe: 'queue', 0x449238: 'set', 0x43d0ce: 'flags',
                    0x43d574: 'extended', 0x43ce9e: 'simple'} if native else
                   {0x101010: 'queue', 0x101020: 'set', 0x101030: 'flags',
                    0x101040: 'extended', 0x101050: 'simple'})
        calls = []
        done = [False]

        def cstring(pointer):
            value = bytearray()
            for offset in range(256):
                byte = machine.mem_read(pointer + offset, 1)[0]
                if not byte:
                    break
                value.append(byte)
            return bytes(value)

        def callback(unit, pc, _size, _user):
            if pc == 0x101180:
                done[0] = True
                unit.emu_stop()
                return
            kind = targets.get(pc)
            if kind is None:
                return
            r0, r1, r2, r3 = (unit.reg_read(getattr(A, f'UC_ARM_REG_R{i}')) for i in range(4))
            if kind == 'queue':
                calls.append((kind, r0, r1, r2, r3))
                unit.reg_write(A.UC_ARM_REG_R0, status & 0xffffffff)
            elif kind == 'set':
                calls.append((kind, r0, r1))
                unit.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind == 'flags':
                calls.append((kind,))
                unit.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == 'extended':
                sp = unit.reg_read(A.UC_ARM_REG_SP)
                args = [int.from_bytes(unit.mem_read(sp + 4*i, 4), 'little') for i in range(3)]
                calls.append((kind, r0, cstring(r1), cstring(r2), cstring(r3),
                              args[0], cstring(args[1]), args[2]))
            else:
                calls.append((kind, r0, cstring(r1), cstring(r2), r3))
            unit.reg_write(A.UC_ARM_REG_PC, unit.reg_read(A.UC_ARM_REG_LR))

        machine.hook_add(UC_HOOK_CODE, callback)
        entry = 0x53c638 if native else symbols['stock_audio_submit']
        machine.emu_start(entry | 1, 0, count=300)
        assert done[0], (native, message, queue, status, flags)
        return calls

    count = 0
    for message in (0, 0x20007000):
        for queue in (0, 0x20006000):
            for status in (0, 1, 0xfffffffe):
                for flags in (0, 1, 2, 3, 4, 5, 6, 7):
                    original = run(True, message, queue, status, flags)
                    candidate = run(False, message, queue, status, flags)
                    assert original == candidate, (message, queue, status, flags, original, candidate)
                    count += 1
    print('PASS_AUDIO_SUBMIT', count)
