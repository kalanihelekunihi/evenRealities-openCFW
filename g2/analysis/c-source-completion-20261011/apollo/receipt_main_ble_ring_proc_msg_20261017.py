#!/usr/bin/env python3
"""Integrate four stock-matched BLE ring client C entries into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-ble-ring-proc-msg'
PRIOR = BASE / 'main-attc-write-command/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_ring_proc_msg_4c4910.c'
ORACLE = HERE / 'oracle.json'
OBJECT, CURRENT, OUT = HERE / 'ring-proc.o', HERE / 'candidate.o', HERE / 'receipt.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def undefined(path):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle['status'] == 'PASS_MAIN_BLE_RING_PROC_MSG_BOUNDED_STOCK_MATCH'
    assert oracle['cases'] == 5760 and oracle['source_sha256'] == sha(SOURCE)
    assert oracle['stock_entries'] == {'token': '0x4c46c0', 'enable': '0x4c46d0',
                                       'receive': '0x4c48ac', 'message': '0x4c4910'}
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    before, after = set(undefined(PRIOR)), set(undefined(CURRENT))
    removed, added = sorted(before - after), sorted(after - before)
    assert removed == ['audio_ble_master_message'] and not added
    assert len(before) == 84 and len(after) == 83
    record = {
        'status': 'PASS_MAIN_BLE_RING_PROC_MSG_C_INTEGRATION',
        'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
        'ring_object': ref(OBJECT), 'source': ref(SOURCE), 'oracle': ref(ORACLE),
        'native_decomp': [ref(ROOT / f'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/decomp/{address}.c')
                          for address in ('004c46c0', '004c46d0', '004c48ac', '004c4910')],
        'unresolved_before': 84, 'unresolved_after': 83,
        'removed_imports': removed, 'new_imports': added,
        'remaining_gate': 'The ring token, CCCD enable, receive and message dispatcher C bodies match 5760 bounded stock cases. ATT, event-loop, ring-task, logging and DM lower children were controlled; full runtime and image gates remain.',
        'source_complete': False, 'flashable': False, 'hardware_proof': False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
