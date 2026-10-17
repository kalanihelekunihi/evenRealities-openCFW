#!/usr/bin/env python3
"""Compare both C settings version children with authenticated stock entries."""
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
HERE = ROOT / 'g2/build/c-firmware/20261017/main-settings-version-children'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_version_sync_children_20261017.c'
VERSION = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_version_text.c'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
RAM = 0x20072da8
CHILDREN = {'copy': 0x44b5a0, 'zero': 0x43c0e4, 'peer': 0x465480,
            'notify': 0x49be04, 'flags': 0x43d0ce,
            'extended': 0x43d574, 'compact': 0x43ce9e}
REGS = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)
ENTRIES = {'update': (0x46baec, 'audio_settings_update_left_version'),
           'send': (0x46b988, 'audio_settings_sync_version_only_send')}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word(u, address):
    return struct.unpack('<I', u.mem_read(address, 4))[0]


def text_at(u, address):
    return bytes(u.mem_read(address, 180)).split(b'\0', 1)[0].decode(errors='replace')


def compile_candidate():
    HERE.mkdir(parents=True, exist_ok=True)
    link = HERE / 'oracle.ld'
    binding_names = {'audio_settings_copy_text': 'copy',
                     'audio_uart_buffer_zero': 'zero',
                     'audio_settings_send_peer_packet': 'peer',
                     'audio_settings_notify_device_status': 'notify',
                     'audio_log_flags': 'flags',
                     'audio_log_extended': 'extended',
                     'compressed_log_output': 'compact'}
    bindings = ' '.join(f'{name} = {CHILDREN[kind] | 1:#x};'
                        for name, kind in binding_names.items())
    link.write_text(f'audio_settings_config_live = {RAM:#x}; {bindings} '
                    'SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } '
                    '/DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
    elf = HERE / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-std=c11', '-O2', '-ffreestanding', '-fno-builtin',
                    '-nostdlib', '-Wl,-T,' + str(link), str(SOURCE), str(VERSION),
                    '-o', str(elf)], check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    with elf.open('rb') as stream:
        image = ELFFile(stream)
        symbols = {s.name: s['st_value'] for s in image.get_section_by_name('.symtab').iter_symbols()}
        segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
    return elf, symbols, segments


def run(native, kind, symbols, segments, stock, version, prior, flags):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.mem_map(0x438000, (len(stock) + 4095) & ~4095)
    u.mem_write(0x438000, stock)
    u.mem_map(0x20000000, 0x80000)
    u.mem_map(0x100000, 0x10000)
    for address, data in segments:
        u.mem_write(address, data)
    config = bytearray(0x50)
    config[0x44] = prior
    u.mem_write(RAM, bytes(config))
    u.mem_write(0x20003000, version)
    u.reg_write(UC_ARM_REG_R0, 0 if version[0] == 0xff else 0x20003000)
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x2007f001)
    trace = []
    by_address = {address: name for name, address in CHILDREN.items()}

    def code_hook(emu, address, size, user_data):
        child = by_address.get(address)
        if child is None:
            return
        args = [emu.reg_read(reg) for reg in REGS]
        if child == 'flags':
            trace.append((child,))
            emu.reg_write(UC_ARM_REG_R0, flags)
        elif child == 'zero':
            trace.append((child, args[1], args[2]))
            emu.mem_write(args[0], bytes([args[2] & 0xff]) * args[1])
        elif child == 'copy':
            trace.append((child, args[2], bytes(emu.mem_read(args[1], args[2])).hex()))
            emu.mem_write(args[0], bytes(emu.mem_read(args[1], args[2])))
            emu.reg_write(UC_ARM_REG_R0, args[0])
        elif child == 'peer':
            trace.append((child, args[0], args[2], args[3],
                          word(emu, emu.reg_read(UC_ARM_REG_SP)),
                          bytes(emu.mem_read(args[1], args[2])).hex()))
            emu.reg_write(UC_ARM_REG_R0, 0)
        elif child == 'extended':
            sp = emu.reg_read(UC_ARM_REG_SP)
            trace.append((child, args[0], word(emu, sp),
                          text_at(emu, word(emu, sp + 4))))
        elif child == 'compact':
            trace.append((child, args[0], text_at(emu, args[1])))
        else:
            trace.append((child,))
        emu.reg_write(UC_ARM_REG_PC, emu.reg_read(UC_ARM_REG_LR))

    u.hook_add(UC_HOOK_CODE, code_hook)
    original, generated = ENTRIES[kind]
    u.emu_start((original if native else symbols[generated]) | 1,
                0x2007f000, count=20000)
    assert u.reg_read(UC_ARM_REG_PC) == 0x2007f000
    return {'trace': trace, 'config': bytes(u.mem_read(RAM, 0x50)).hex()}


def main():
    stock = STOCK.read_bytes()[32:]
    assert hashlib.sha256(stock).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
    elf, symbols, segments = compile_candidate()
    count = 0
    for kind, version, prior, flags in itertools.product(
            ('update', 'send'), (b'\xff' + b'\0' * 15,
                                  b'\0' * 16, b'2.2.6.10\0' + b'\0' * 7),
            (0, ord('1')), (0, 1, 2, 4, 7)):
        stock_result = run(True, kind, symbols, segments, stock, version, prior, flags)
        c_result = run(False, kind, symbols, segments, stock, version, prior, flags)
        assert stock_result == c_result, (kind, version, prior, flags,
                                          stock_result, c_result)
        count += 1
    record = {'status': 'PASS_MAIN_SETTINGS_VERSION_CHILDREN_BOUNDED_STOCK_MATCH',
              'cases': count, 'source_sha256': sha(SOURCE),
              'version_source_sha256': sha(VERSION), 'oracle_elf_sha256': sha(elf),
              'stock_payload_sha256': hashlib.sha256(stock).hexdigest(),
              'stock_entries': {key: hex(value[0]) for key, value in ENTRIES.items()},
              'controlled_children': CHILDREN,
              'limits': ['Peer send, copy, logging and notification are controlled child boundaries.',
                         'Full peer delivery, persistence, RAM placement and hardware behavior remain unproven.'],
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    output = HERE / 'oracle.json'
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], count, sha(output))


if __name__ == '__main__':
    main()
