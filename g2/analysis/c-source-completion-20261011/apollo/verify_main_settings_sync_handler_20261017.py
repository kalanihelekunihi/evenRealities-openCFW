#!/usr/bin/env python3
"""Compare stock and C settings sync dispatch with controlled child calls."""
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
HERE = ROOT / 'g2/build/c-firmware/20261017/main-settings-sync-handler'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_sync_handler_46bbb4.c'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
ENTRY = 0x46bbb4
RAM = 0x20072da8
CHILDREN = {
    'role': 0x45a568, 'copy': 0x439c04, 'mode': 0x46c630,
    'set_mode': 0x46c63c, 'dump': 0x46b458, 'apply': 0x46b912,
    'send': 0x46b930, 'left_version': 0x46baec, 'version_send': 0x46b988,
    'flags': 0x43d0ce, 'extended': 0x43d574, 'compact': 0x43ce9e,
}
REGS = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word(u, address):
    return struct.unpack('<I', u.mem_read(address, 4))[0]


def put(u, address, value):
    u.mem_write(address, struct.pack('<I', value & 0xffffffff))


def cstring(u, address):
    return bytes(u.mem_read(address, 160)).split(b'\0', 1)[0].decode(errors='replace')


def compile_candidate():
    HERE.mkdir(parents=True, exist_ok=True)
    script = HERE / 'oracle.ld'
    bindings = ' '.join(f'{name} = {address | 1:#x};' for name, address in {
        'audio_uart_device_role_get': CHILDREN['role'],
        'audio_uart_checksum_copy': CHILDREN['copy'],
        'audio_settings_terminal_mode': CHILDREN['mode'],
        'audio_settings_terminal_mode_set': CHILDREN['set_mode'],
        'SVC_Settings_DumpSettingConfig': CHILDREN['dump'],
        'audio_settings_apply_display_levels': CHILDREN['apply'],
        'audio_settings_send_config_to_peer': CHILDREN['send'],
        'audio_settings_update_left_version': CHILDREN['left_version'],
        'audio_settings_sync_version_only_send': CHILDREN['version_send'],
        'audio_log_flags': CHILDREN['flags'],
        'audio_log_extended': CHILDREN['extended'],
        'compressed_log_output': CHILDREN['compact'],
    }.items())
    script.write_text(f'audio_settings_config_live = {RAM:#x}; {bindings} '
                      'SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } '
                      '/DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
    elf = HERE / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-std=c11', '-O2', '-ffreestanding', '-fno-builtin',
                    '-nostdlib', '-Wl,-T,' + str(script), str(SOURCE), '-o', str(elf)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with elf.open('rb') as stream:
        image = ELFFile(stream)
        entry = next(s['st_value'] for s in image.get_section_by_name('.symtab').iter_symbols()
                     if s.name == 'audio_setting_handle_command5_46bbb4')
        segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
    return elf, entry, segments


def run(native, entry, segments, payload, length, msg_type, role, flags,
        crc_match, mode_change, null_payload, prior_version=0,
        new_version=b'2.2.6.10\0'):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.mem_map(0x438000, (len(payload) + 4095) & ~4095)
    u.mem_write(0x438000, payload)
    u.mem_map(0x20000000, 0x80000)
    u.mem_map(0x100000, 0x10000)
    for address, data in segments:
        u.mem_write(address, data)
    config = bytearray(0x50)
    config[0x1d] = 0 if mode_change else 1
    config[0x18:0x1a] = b'\x34\x12'
    config[0x44] = prior_version
    u.mem_write(RAM, bytes(config))
    buffer = bytearray(48)
    buffer[0] = msg_type
    buffer[0x21] = 1
    buffer[0x1c:0x1e] = b'\x34\x12' if crc_match else b'\x78\x56'
    buffer[36:45] = new_version[:9]
    u.mem_write(0x20002000, bytes(buffer))
    u.reg_write(UC_ARM_REG_R0, 0 if null_payload else 0x20002000)
    u.reg_write(UC_ARM_REG_R1, length)
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x2007f001)
    trace = []
    by_address = {value: key for key, value in CHILDREN.items()}

    def code_hook(emu, address, size, user_data):
        kind = by_address.get(address)
        if kind is None:
            return
        args = [emu.reg_read(reg) for reg in REGS]
        if kind == 'flags':
            trace.append((kind,))
            emu.reg_write(UC_ARM_REG_R0, flags)
        elif kind == 'role':
            trace.append((kind,))
            emu.reg_write(UC_ARM_REG_R0, role)
        elif kind == 'mode':
            trace.append((kind,))
            emu.reg_write(UC_ARM_REG_R0, emu.mem_read(RAM + 0x1d, 1)[0])
        elif kind == 'copy':
            trace.append((kind, args[2]))
            emu.mem_write(args[0], bytes(emu.mem_read(args[1], args[2])))
        elif kind == 'copy_text':
            trace.append((kind, args[2], bytes(emu.mem_read(args[1], args[2])).hex()))
            emu.mem_write(args[0], bytes(emu.mem_read(args[1], args[2])))
            emu.reg_write(UC_ARM_REG_R0, args[0])
        elif kind == 'zero':
            trace.append((kind, args[1], args[2]))
            emu.mem_write(args[0], bytes([args[2] & 0xff]) * args[1])
        elif kind == 'peer':
            trace.append((kind, args[0], args[2], args[3],
                          word(emu, emu.reg_read(UC_ARM_REG_SP)),
                          bytes(emu.mem_read(args[1], args[2])).hex()))
            emu.reg_write(UC_ARM_REG_R0, 0)
        elif kind == 'set_mode':
            trace.append((kind, args[0] & 0xff))
            emu.mem_write(RAM + 0x1d, bytes([args[0] & 0xff]))
        elif kind == 'extended':
            stack = emu.reg_read(UC_ARM_REG_SP)
            trace.append((kind, args[0], word(emu, stack),
                          cstring(emu, word(emu, stack + 4))))
        elif kind == 'compact':
            trace.append((kind, args[0], cstring(emu, args[1])))
        else:
            trace.append((kind,))
        emu.reg_write(UC_ARM_REG_PC, emu.reg_read(UC_ARM_REG_LR))

    u.hook_add(UC_HOOK_CODE, code_hook)
    u.emu_start((ENTRY if native else entry) | 1, 0x2007f000, count=20000)
    assert u.reg_read(UC_ARM_REG_PC) == 0x2007f000
    return {'trace': trace, 'config': bytes(u.mem_read(RAM, 0x50)).hex()}


def main():
    raw = STOCK.read_bytes()[32:]
    assert hashlib.sha256(raw).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
    elf, entry, segments = compile_candidate()
    cases = 0
    for length, msg_type, role, flags, crc_match, mode_change, null_payload in itertools.product(
            [0, 47, 48], [0, 1, 2, 3, 4], [1, 2], [0, 1, 2, 4, 7],
            [False, True], [False, True], [False, True]):
        stock = run(True, entry, segments, raw, length, msg_type, role, flags,
                    crc_match, mode_change, null_payload)
        candidate = run(False, entry, segments, raw, length, msg_type, role, flags,
                        crc_match, mode_change, null_payload)
        assert stock == candidate, (length, msg_type, role, flags, crc_match, mode_change,
                                    null_payload,
                                    stock, candidate)
        cases += 1
    record = {'status': 'PASS_MAIN_SETTINGS_SYNC_HANDLER_BOUNDED_STOCK_MATCH',
              'cases': cases, 'source_sha256': sha(SOURCE), 'oracle_elf_sha256': sha(elf),
              'stock_payload_sha256': hashlib.sha256(raw).hexdigest(),
              'stock_entry': hex(ENTRY),
              'controlled_children': CHILDREN,
              'limits': ['Version children and logging callees are controlled call boundaries.',
                         'No physical BLE peer, flash persistence, or complete image behavior is proven.'],
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    output = HERE / 'oracle.json'
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], cases, sha(output))


if __name__ == '__main__':
    main()
