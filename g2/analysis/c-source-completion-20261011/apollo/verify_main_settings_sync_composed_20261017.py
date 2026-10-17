#!/usr/bin/env python3
"""Run dispatcher and both version children together against the stock chain."""
import hashlib
import importlib.util
import itertools
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
HERE = ROOT / 'g2/build/c-firmware/20261017/main-settings-sync-composed'
DISPATCH = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_sync_handler_46bbb4.c'
CHILDREN_SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_version_sync_children_20261017.c'
VERSION = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_version_text.c'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE = Path(__file__).with_name('verify_main_settings_sync_handler_20261017.py')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_base():
    spec = importlib.util.spec_from_file_location('settings_sync_base', BASE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.CHILDREN.pop('left_version')
    module.CHILDREN.pop('version_send')
    module.CHILDREN.update({'copy_text': 0x44b5a0, 'zero': 0x43c0e4,
                            'peer': 0x465480, 'notify': 0x49be04})
    return module


def compile_candidate(base):
    HERE.mkdir(parents=True, exist_ok=True)
    link = HERE / 'oracle.ld'
    names = {
        'audio_uart_device_role_get': 'role',
        'audio_uart_checksum_copy': 'copy',
        'audio_settings_terminal_mode': 'mode',
        'audio_settings_terminal_mode_set': 'set_mode',
        'SVC_Settings_DumpSettingConfig': 'dump',
        'audio_settings_apply_display_levels': 'apply',
        'audio_settings_send_config_to_peer': 'send',
        'audio_log_flags': 'flags',
        'audio_log_extended': 'extended',
        'compressed_log_output': 'compact',
        'audio_settings_copy_text': 'copy_text',
        'audio_uart_buffer_zero': 'zero',
        'audio_settings_send_peer_packet': 'peer',
        'audio_settings_notify_device_status': 'notify',
    }
    bindings = ' '.join(f'{name} = {base.CHILDREN[kind] | 1:#x};'
                        for name, kind in names.items())
    link.write_text(f'audio_settings_config_live = {base.RAM:#x}; {bindings} '
                    'SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } '
                    '/DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
    elf = HERE / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-std=c11', '-O2', '-ffreestanding', '-fno-builtin',
                    '-nostdlib', '-Wl,-T,' + str(link), str(DISPATCH),
                    str(CHILDREN_SOURCE), str(VERSION), '-o', str(elf)],
                   check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    with elf.open('rb') as stream:
        image = ELFFile(stream)
        entry = next(s['st_value'] for s in image.get_section_by_name('.symtab').iter_symbols()
                     if s.name == 'audio_setting_handle_command5_46bbb4')
        segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
    return elf, entry, segments


def main():
    base = load_base()
    raw = STOCK.read_bytes()[32:]
    assert hashlib.sha256(raw).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
    elf, entry, segments = compile_candidate(base)
    count = 0
    for (length, msg_type, role, flags, crc_match, mode_change, null_payload,
         prior_version) in itertools.product(
                [0, 47, 48], [0, 1, 2, 3, 4], [1, 2], [0, 1, 2, 4, 7],
                [False, True], [False, True], [False, True], [0, ord('1')]):
        params = (entry, segments, raw, length, msg_type, role, flags,
                  crc_match, mode_change, null_payload, prior_version)
        original = base.run(True, *params)
        compiled = base.run(False, *params)
        assert original == compiled, (length, msg_type, role, flags,
                                      crc_match, mode_change, null_payload,
                                      prior_version, original, compiled)
        count += 1
    record = {
        'status': 'PASS_MAIN_SETTINGS_SYNC_COMPOSED_STOCK_MATCH',
        'cases': count,
        'dispatcher_source_sha256': sha(DISPATCH),
        'version_children_source_sha256': sha(CHILDREN_SOURCE),
        'version_text_source_sha256': sha(VERSION),
        'oracle_elf_sha256': sha(elf),
        'stock_payload_sha256': hashlib.sha256(raw).hexdigest(),
        'stock_dispatcher_entry': '0x46bbb4',
        'controlled_lower_children': base.CHILDREN,
        'limits': ['Lower level BLE send, notification, logging and copy calls are controlled boundaries.',
                   'No physical peer, persistence, final placement or hardware proof.'],
        'source_complete': False, 'flashable': False, 'hardware_proof': False,
    }
    output = HERE / 'oracle.json'
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], count, sha(output))


if __name__ == '__main__':
    main()
