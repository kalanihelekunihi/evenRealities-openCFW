#!/usr/bin/env python3
"""Source-own the two remaining 16-byte BLE connection profiles."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-conn-param-profiles'
PRIOR = BASE / 'main-ble-ring-proc-msg/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_conn_param_profile_records_20261017.c'
MIDDLE = ROOT / 'g2/components/audio/uart_thread_source_candidate/ble_msgtx_table.c'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OBJECT, CURRENT, OUT = HERE / 'profiles.o', HERE / 'candidate.o', HERE / 'receipt.json'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def section_bytes(path, section):
    with path.open('rb') as stream:
        image = ELFFile(stream)
        selected = image.get_section_by_name(section)
        assert selected is not None
        return selected.data()


def undefined(path):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines() if line.strip()})


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    assert 'audio_ble_msgtx_table[16]' in MIDDLE.read_text()
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    rows = []
    for address, section, symbol in (
            (0x784ea0, '.g2_rom_00784ea0', 'audio_ble_conn_param_slow_profile_784ea0'),
            (0x784eb0, '.g2_rom_00784eb0', 'audio_ble_msgtx_table'),
            (0x784ec0, '.g2_rom_00784ec0', 'audio_ble_conn_param_fast_profile_784ec0')):
        observed = section_bytes(OBJECT if address != 0x784eb0 else PRIOR, section)
        expected = payload[address - 0x438000:address - 0x438000 + 16]
        assert len(observed) == 16 and observed == expected
        rows.append({'stock_address': hex(address), 'section': section,
                     'symbol': symbol, 'stock_bytes': expected.hex()})
    pointers = {'slow': (0x4786c8, 0x784ea0),
                'fast_initial': (0x47871c, 0x784eb0),
                'fast_active': (0x478760, 0x784ec0)}
    for literal, target in pointers.values():
        offset = literal - 0x438000
        assert int.from_bytes(payload[offset:offset + 4], 'little') == target
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    assert undefined(PRIOR) == undefined(CURRENT)
    assert len(undefined(CURRENT)) == 83
    record = {
        'status': 'PASS_MAIN_CONN_PARAM_PROFILE_RECORDS_C_INTEGRATION',
        'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
        'profile_object': ref(OBJECT), 'source': ref(SOURCE),
        'existing_middle_source': ref(MIDDLE),
        'stock_payload_sha256': PAYLOAD_SHA,
        'records': rows,
        'literal_targets': {key: {'literal': hex(value[0]), 'target': hex(value[1])}
                            for key, value in pointers.items()},
        'unresolved_before': 83, 'unresolved_after': 83,
        'removed_imports': [], 'new_imports': [],
        'remaining_gate': 'All three bounded 16-byte connection-parameter profile records are source-owned and stock-byte matched. The APP_ConnectParamHandler dispatcher and its children still need C bodies and composition checks; final placement and hardware behavior remain open.',
        'source_complete': False, 'flashable': False, 'hardware_proof': False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(undefined(CURRENT)), sha(OUT))


if __name__ == '__main__':
    main()
