#!/usr/bin/env python3
"""Add the stock-matched Cordio ATT write command to Main C providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-attc-write-command'
PRIOR = BASE / 'main-settings-version-children/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_att_write_command_539dea.c'
ORACLE = HERE / 'oracle.json'
OBJECT, CURRENT, OUT = HERE / 'command.o', HERE / 'candidate.o', HERE / 'receipt.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def undefined(path):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle['status'] == 'PASS_MAIN_ATTC_WRITE_COMMAND_BOUNDED_STOCK_MATCH'
    assert oracle['cases'] == 60 and oracle['source_sha256'] == sha(SOURCE)
    assert oracle['stock_entry'] == '0x539dea'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    before, after = undefined(PRIOR), undefined(CURRENT)
    assert before == after and len(after) == 84
    defined = subprocess.check_output(['arm-none-eabi-nm', '-g', '--defined-only',
                                       str(CURRENT)], text=True)
    assert ' audio_ble_attc_write_command_539dea' in defined
    record = {'status': 'PASS_MAIN_ATTC_WRITE_COMMAND_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'command_object': ref(OBJECT), 'source': ref(SOURCE),
              'oracle': ref(ORACLE),
              'native_decomp': ref(ROOT / 'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/decomp/00539dea.c'),
              'unresolved_before': 84, 'unresolved_after': 84,
              'removed_imports': [], 'new_imports': [],
              'remaining_gate': 'The Cordio ATT write-command C body matches 60 bounded stock allocation, frame and send cases. The ring dispatcher that calls it remains unresolved; real ATT transport, final placement and device behavior remain open.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
