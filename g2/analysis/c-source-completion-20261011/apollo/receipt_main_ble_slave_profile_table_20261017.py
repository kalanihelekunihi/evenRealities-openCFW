#!/usr/bin/env python3
"""Bind the one-byte stock Cordio slave profile configuration."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CORDIO = ROOT / 'third-party/upstream/cordio'
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-ble-slave-profile-table'
PRIOR = BASE / 'main-ble-ota-dm-state-alias/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_slave_profile_table_78f6d2_20261017.c'
HEADER = CORDIO / 'ble-profiles/include/app_api.h'
ADV_SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_app_adv_start.c'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OBJECT, CURRENT, OUT = HERE / 'slave-profile.o', HERE / 'candidate.o', HERE / 'receipt.json'
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
    assert payload[0x78f6d2 - 0x438000] == 1
    assert 'uint8_t     connMax;' in HEADER.read_text()
    assert 'audio_ble_slave_profile_slot[0]' in ADV_SOURCE.read_text()
    assert subprocess.check_output(['git', '-C', str(CORDIO), 'rev-parse', 'HEAD'],
                                   text=True).strip() == '3656312d6b73e2a2c1c8b33ee0385bc199dd97e6'
    dirs = [CORDIO / 'wsf/include', CORDIO / 'ble-host/include',
            CORDIO / 'ble-profiles/include']
    dirs += sorted({p.parent for p in CORDIO.rglob('*.h')})
    flags = []
    for path in dict.fromkeys(dirs):
        flags += ['-I', str(path)]
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', *flags, '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    sections = subprocess.check_output(['arm-none-eabi-objdump', '-h', str(OBJECT)], text=True)
    assert '.g2_flash_0078f6d2 00000001' in sections
    data = subprocess.check_output(['arm-none-eabi-objdump', '-s', '-j',
                                    '.g2_flash_0078f6d2', str(OBJECT)], text=True)
    assert '01' in data
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert removed == ['audio_ble_slave_profile_table'] and not added
    assert len(prior) == 89 and len(after) == 88
    record = {'status': 'PASS_MAIN_BLE_SLAVE_PROFILE_TABLE_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SOURCE), 'cordio_header': ref(HEADER),
              'advertising_source': ref(ADV_SOURCE),
              'stock_payload_sha256': PAYLOAD_SHA,
              'stock_address': '0x78f6d2', 'stock_byte': '01',
              'type': 'appSlaveCfg_t', 'extent_bytes': 1,
              'unresolved_before': 89, 'unresolved_after': 88,
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'The one-byte Cordio slave connMax config is source-owned and matches authenticated ROM. Final placement, adjacent product data ownership and whole-image behavior remain open.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
