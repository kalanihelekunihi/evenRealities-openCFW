#!/usr/bin/env python3
"""Bind native radio stack row storage into experimental Main C candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-ble-vendor-stack-rows'
PRIOR = BASE / 'main-ble-master-registration-table/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_vendor_stack_rows_2003b558_20261017.c'
DAEMON = ROOT / 'g2/components/audio/source_candidate_20261010/daemon_static_memory.c'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OBJECT, CURRENT, OUT = HERE / 'stack-rows.o', HERE / 'candidate.o', HERE / 'receipt.json'
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
    offset = 0x55cc18 - 0x438000
    assert payload[offset:offset + 4] == (0x2003b558).to_bytes(4, 'little')
    assert '0x2003fa98u' in DAEMON.read_text()
    assert 0x2003b558 + 8 * 0x8a8 == 0x2003fa98
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    sections = subprocess.check_output(['arm-none-eabi-objdump', '-h', str(OBJECT)], text=True)
    assert '.g2_bss_2003b558 00004540' in sections
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert removed == ['audio_ble_vendor_stack_rows_2003b558'] and not added
    assert len(prior) == 93 and len(after) == 92
    record = {'status': 'PASS_MAIN_BLE_VENDOR_STACK_ROWS_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SOURCE), 'boundary_source': ref(DAEMON),
              'stock_payload_sha256': PAYLOAD_SHA,
              'stock_base': '0x2003b558', 'exclusive_end': '0x2003fa98',
              'rows': 8, 'stride': '0x8a8', 'extent_bytes': 0x4540,
              'unresolved_before': 93, 'unresolved_after': 92,
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'Eight complete radio-stack row storage extents compile as BSS. Stock pointer and adjacent daemon-stack boundary agree; startup zeroing, final placement and whole-image behavior remain unproven.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
