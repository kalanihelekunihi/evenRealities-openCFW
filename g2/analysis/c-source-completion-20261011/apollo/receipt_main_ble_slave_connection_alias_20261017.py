#!/usr/bin/env python3
"""Bind slave connection-info name to the existing mode-context pointer cell."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-ble-slave-connection-alias'
PRIOR = BASE / 'main-ble-slave-profile-table/candidate.o'
STATE_SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_slave_pointer_cells.c'
PRODUCER = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_slave_handler_init.c'
CONSUMER = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_role_ota.c'
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
    assert (0x20074330).to_bytes(4, 'little') in payload
    assert 'uint8_t *audio_ble_slave_mode_context;' in STATE_SOURCE.read_text()
    assert 'audio_ble_slave_mode_context=mode;' in PRODUCER.read_text()
    assert 'audio_ble_slave_connection_info[31u]' in CONSUMER.read_text()
    prior_nm = subprocess.check_output(['arm-none-eabi-nm', str(PRIOR)], text=True)
    state = [line.split() for line in prior_nm.splitlines()
             if line.split()[-1:] == ['audio_ble_slave_mode_context']]
    assert len(state) == 1 and state[0][1] == 'B'
    offset = int(state[0][0], 16)
    assert 'audio_ble_slave_connection_info' in symbols(PRIOR, '-u')
    size_before = bss_size(PRIOR)
    subprocess.run(['arm-none-eabi-objcopy',
                    f'--add-symbol=audio_ble_slave_connection_info=.bss:0x{offset:x},global',
                    str(PRIOR), str(ALIASED)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-r', str(ALIASED), '-o', str(CURRENT)], check=True)
    assert bss_size(CURRENT) == size_before
    current_nm = subprocess.check_output(['arm-none-eabi-nm', str(CURRENT)], text=True)
    matching = [line.split() for line in current_nm.splitlines()
                if line.split()[-1:] in (['audio_ble_slave_mode_context'],
                                         ['audio_ble_slave_connection_info'])]
    assert len(matching) == 2 and all(int(row[0], 16) == offset and row[1] == 'B'
                                      for row in matching)
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert removed == ['audio_ble_slave_connection_info'] and not added
    assert len(prior) == 88 and len(after) == 87
    record = {'status': 'PASS_MAIN_BLE_SLAVE_CONNECTION_ALIAS_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'state_source': ref(STATE_SOURCE), 'producer_source': ref(PRODUCER),
              'consumer_source': ref(CONSUMER),
              'stock_payload_sha256': PAYLOAD_SHA,
              'stock_pointer_cell': '0x20074330', 'bss_symbol_offset': hex(offset),
              'bss_size_unchanged': size_before,
              'unresolved_before': 88, 'unresolved_after': 87,
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'Slave connection-info and mode-context names share the same C-owned pointer cell at native 0x20074330. Final absolute RAM placement, runtime pointer lifetime and whole-image gates remain.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
