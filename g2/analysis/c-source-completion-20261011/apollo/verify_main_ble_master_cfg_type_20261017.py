#!/usr/bin/env python3
"""Check tracked Cordio appMasterCfg_t layout against stock Main ROM."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CORDIO = ROOT / 'third-party/upstream/cordio'
HERE = ROOT / 'g2/build/c-firmware/20261017/main-ble-master-registration-table'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_master_registration_table_78c9e4_20261017.c'
CURRENT_OBJECT = HERE / 'registration-table.o'
HEADER = CORDIO / 'ble-profiles/include/app_api.h'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = HERE / 'typed-config-oracle.json'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    stock = payload[0x78c9e4 - 0x438000:0x78c9ec - 0x438000]
    assert stock == bytes.fromhex('a000800010270001')
    assert subprocess.check_output(['git', '-C', str(CORDIO), 'rev-parse', 'HEAD'],
                                   text=True).strip() == '3656312d6b73e2a2c1c8b33ee0385bc199dd97e6'
    dirs = [CORDIO / 'wsf/include', CORDIO / 'ble-host/include',
            CORDIO / 'ble-profiles/include']
    dirs += sorted({p.parent for p in CORDIO.rglob('*.h')})
    flags = []
    for path in dict.fromkeys(dirs):
        flags += ['-I', str(path)]
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        typed_source = directory / 'master_cfg.c'
        typed_object = directory / 'master_cfg.o'
        typed_bytes = directory / 'typed.bin'
        selected_bytes = directory / 'selected.bin'
        typed_source.write_text('''#include "app_api.h"
_Static_assert(sizeof(appMasterCfg_t) == 8u, "stock master config size");
__attribute__((used,section(".g2_master_cfg")))
const appMasterCfg_t g2_typed_master_cfg = {0xa0u, 0x80u, 0x2710u, 0u, 1u};
''')
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                        '-ffreestanding', '-fno-builtin', *flags, '-c',
                        str(typed_source), '-o', str(typed_object)], check=True)
        subprocess.run(['arm-none-eabi-objcopy',
                        f'--dump-section=.g2_master_cfg={typed_bytes}',
                        str(typed_object)], check=True)
        subprocess.run(['arm-none-eabi-objcopy',
                        f'--dump-section=.g2_flash_0078c9e4={selected_bytes}',
                        str(CURRENT_OBJECT)], check=True)
        assert typed_bytes.read_bytes() == selected_bytes.read_bytes() == stock
    record = {'status': 'PASS_MAIN_BLE_MASTER_CFG_TYPED_STOCK_MATCH',
              'stock_payload_sha256': PAYLOAD_SHA,
              'source_sha256': sha(SOURCE.read_bytes()),
              'cordio_header_sha256': sha(HEADER.read_bytes()),
              'cordio_commit': '3656312d6b73e2a2c1c8b33ee0385bc199dd97e6',
              'type': 'appMasterCfg_t', 'size_bytes': 8,
              'fields': {'scanInterval': 160, 'scanWindow': 128,
                         'scanDuration': 10000, 'discMode': 0, 'scanType': 1},
              'stock_address': '0x78c9e4', 'stock_bytes': stock.hex(),
              'scope': 'Full typed Cordio master config record matches selected C and authenticated stock bytes.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], sha(OUT.read_bytes()))


if __name__ == '__main__':
    main()
