#!/usr/bin/env python3
"""Verify and bind the bounded BLE master registration ROM record."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-ble-master-registration-table'
PRIOR = BASE / 'main-ble-cordio-api-aliases/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_master_registration_table_78c9e4_20261017.c'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OBJECT, CURRENT, OUT = HERE / 'registration-table.o', HERE / 'candidate.o', HERE / 'receipt.json'
TYPED_ORACLE = HERE / 'typed-config-oracle.json'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', option, str(path)], text=True).splitlines() if line.strip()})


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    offset = 0x78c9e4 - 0x438000
    stock = payload[offset:offset + 8]
    assert stock == bytes.fromhex('a000800010270001')
    assert payload[offset + 8:offset + 16] == b'ble.mgr\0'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    section = subprocess.check_output(['arm-none-eabi-objdump', '-s', '-j',
                                       '.g2_flash_0078c9e4', str(OBJECT)], text=True)
    assert 'a0008000 10270001' in section
    typed = json.loads(TYPED_ORACLE.read_text())
    assert typed['status'] == 'PASS_MAIN_BLE_MASTER_CFG_TYPED_STOCK_MATCH'
    assert typed['source_sha256'] == sha(SOURCE)
    assert typed['type'] == 'appMasterCfg_t' and typed['size_bytes'] == 8
    assert typed['stock_bytes'] == stock.hex()
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert removed == ['audio_ble_master_registration_table'] and not added
    assert len(prior) == 94 and len(after) == 93
    record = {'status': 'PASS_MAIN_BLE_MASTER_REGISTRATION_TABLE_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SOURCE), 'typed_config_oracle': ref(TYPED_ORACLE),
              'stock_payload_sha256': PAYLOAD_SHA,
              'stock_address': '0x78c9e4', 'stock_bytes': stock.hex(),
              'following_boundary': 'ble.mgr\\0 at 0x78c9ec',
              'unresolved_before': 94, 'unresolved_after': 93,
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'All eight bytes and Cordio appMasterCfg_t field meanings are source-owned and stock matched. Whole-image placement and hardware behavior remain unproven.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
