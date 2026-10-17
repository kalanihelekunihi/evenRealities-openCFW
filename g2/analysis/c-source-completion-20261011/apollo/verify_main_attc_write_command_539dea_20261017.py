#!/usr/bin/env python3
"""Compare the C Cordio ATT write-command frame to authenticated stock."""
import hashlib
import itertools
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3, UC_ARM_REG_LR, UC_ARM_REG_PC,
                               UC_ARM_REG_SP)

ROOT = Path(__file__).resolve().parents[4]
HERE = ROOT / 'g2/build/c-firmware/20261017/main-attc-write-command'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_att_write_command_539dea.c'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
CHILDREN = {'alloc': 0x4b50ae, 'copy': 0x439be4, 'send': 0x4b5640}
ENTRY = 0x539dea
REGS = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_candidate():
    HERE.mkdir(parents=True, exist_ok=True)
    script = HERE / 'oracle.ld'
    script.write_text('audio_ble_att_message_allocate_4b50ae = 0x4b50af; '
                      'audio_queue_copy_bytes = 0x439be5; '
                      'audio_ble_attc_send_message_4b5640 = 0x4b5641; '
                      'SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } '
                      '/DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
    elf = HERE / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-std=c11', '-O2', '-ffreestanding', '-fno-builtin',
                    '-nostdlib', '-Wl,-T,' + str(script), str(SOURCE), '-o', str(elf)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with elf.open('rb') as stream:
        image = ELFFile(stream)
        address = next(s['st_value'] for s in image.get_section_by_name('.symtab').iter_symbols()
                       if s.name == 'audio_ble_attc_write_command_539dea')
        segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
    return elf, address, segments


def run(native, generated, segments, raw, connection, handle, length, allocated):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.mem_map(0x438000, (len(raw) + 4095) & ~4095)
    u.mem_write(0x438000, raw)
    u.mem_map(0x20000000, 0x80000)
    u.mem_map(0x100000, 0x10000)
    for address, data in segments:
        u.mem_write(address, data)
    value = bytes((index * 17 + 3) & 0xff for index in range(max(length, 1)))
    u.mem_write(0x20002000, value)
    u.mem_write(0x20003000, b'\xa5' * (length + 11))
    for register, item in zip(REGS, (connection, handle, length, 0x20002000)):
        u.reg_write(register, item)
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x2007f001)
    calls = []
    by_address = {address: name for name, address in CHILDREN.items()}

    def code_hook(emu, address, size, user_data):
        kind = by_address.get(address)
        if kind is None:
            return
        args = [emu.reg_read(register) for register in REGS]
        if kind == 'alloc':
            calls.append((kind, args[0]))
            emu.reg_write(UC_ARM_REG_R0, 0x20003000 if allocated else 0)
        elif kind == 'copy':
            calls.append((kind, args[2], bytes(emu.mem_read(args[1], args[2])).hex()))
            emu.mem_write(args[0], bytes(emu.mem_read(args[1], args[2])))
            emu.reg_write(UC_ARM_REG_R0, args[0])
        else:
            calls.append((kind, args[0], args[1], args[2], args[3] == 0x20003000,
                          bytes(emu.mem_read(args[3], length + 11)).hex()))
            emu.reg_write(UC_ARM_REG_R0, 0x12345678)
        emu.reg_write(UC_ARM_REG_PC, emu.reg_read(UC_ARM_REG_LR))

    u.hook_add(UC_HOOK_CODE, code_hook)
    u.emu_start((ENTRY if native else generated) | 1, 0x2007f000, count=10000)
    assert u.reg_read(UC_ARM_REG_PC) == 0x2007f000
    return {'calls': calls, 'packet': bytes(u.mem_read(0x20003000, length + 11)).hex(),
            'result': u.reg_read(UC_ARM_REG_R0)}


def main():
    raw = STOCK.read_bytes()[32:]
    assert hashlib.sha256(raw).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
    elf, generated, segments = compile_candidate()
    count = 0
    for connection, handle, length, allocated in itertools.product(
            [1, 3], [0, 0x13, 0xabcd], [0, 1, 2, 20, 255], [False, True]):
        original = run(True, generated, segments, raw, connection, handle,
                       length, allocated)
        candidate = run(False, generated, segments, raw, connection, handle,
                        length, allocated)
        assert original == candidate, (connection, handle, length, allocated,
                                       original, candidate)
        count += 1
    record = {'status': 'PASS_MAIN_ATTC_WRITE_COMMAND_BOUNDED_STOCK_MATCH',
              'cases': count, 'source_sha256': sha(SOURCE),
              'oracle_elf_sha256': sha(elf),
              'stock_payload_sha256': hashlib.sha256(raw).hexdigest(),
              'stock_entry': hex(ENTRY), 'controlled_children': CHILDREN,
              'limits': ['Allocation, copy and ATT send are controlled child boundaries.',
                         'No real ATT link, RAM placement or hardware behavior is proven.'],
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    output = HERE / 'oracle.json'
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], count, sha(output))


if __name__ == '__main__':
    main()
