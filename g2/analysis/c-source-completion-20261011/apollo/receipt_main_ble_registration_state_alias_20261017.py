#!/usr/bin/env python3
"""Bind ATT registration records to the C-owned ATTS state at the same stock RAM base."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-ble-registration-state-alias'
PRIOR = BASE / 'main-ble-vendor-stack-rows/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_att_init.c'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
ALIASED, CURRENT, OUT = HERE / 'with-symbol-alias.o', HERE / 'candidate.o', HERE / 'receipt.json'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', option, str(path)], text=True).splitlines() if line.strip()})


def bss_size(path):
    for line in subprocess.check_output(['arm-none-eabi-objdump', '-h', str(path)],
                                        text=True).splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[1] == '.bss':
            return int(fields[2], 16)
    raise RuntimeError('BSS section missing')


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    assert payload[0x535448 - 0x438000:0x53544c - 0x438000] == (0x2006e5f0).to_bytes(4, 'little')
    source = SOURCE.read_text()
    assert 'uint8_t audio_ble_atts_state[0x268u];' in source
    assert 'group*0xc0u+slot*0x40u' in source
    prior_nm = subprocess.check_output(['arm-none-eabi-nm', str(PRIOR)], text=True)
    state = [line.split() for line in prior_nm.splitlines()
             if line.split()[-1:] == ['audio_ble_atts_state']]
    assert len(state) == 1 and state[0][1] == 'B'
    offset = int(state[0][0], 16)
    assert 'audio_ble_registration_records' in symbols(PRIOR, '-u')
    size_before = bss_size(PRIOR)
    subprocess.run(['arm-none-eabi-objcopy',
                    f'--add-symbol=audio_ble_registration_records=.bss:0x{offset:x},global',
                    str(PRIOR), str(ALIASED)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-r', str(ALIASED), '-o', str(CURRENT)], check=True)
    assert bss_size(CURRENT) == size_before
    current_nm = subprocess.check_output(['arm-none-eabi-nm', str(CURRENT)], text=True)
    matching = [line.split() for line in current_nm.splitlines()
                if line.split()[-1:] in (['audio_ble_atts_state'],
                                         ['audio_ble_registration_records'])]
    assert len(matching) == 2 and all(int(row[0], 16) == offset and row[1] == 'B'
                                      for row in matching)
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert removed == ['audio_ble_registration_records'] and not added
    assert len(prior) == 92 and len(after) == 91
    record = {'status': 'PASS_MAIN_BLE_REGISTRATION_STATE_ALIAS_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'state_source': ref(SOURCE), 'stock_payload_sha256': PAYLOAD_SHA,
              'stock_ram_base': '0x2006e5f0', 'bss_symbol_offset': hex(offset),
              'state_extent_bytes': 0x268, 'bss_size_unchanged': size_before,
              'unresolved_before': 92, 'unresolved_after': 91,
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'Registration records and ATTS state now share one C-owned BSS allocation at the authenticated native base. Final absolute RAM placement, startup zeroing and whole-image behavior remain open.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
