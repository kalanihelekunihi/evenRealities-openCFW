#!/usr/bin/env python3
"""Integrate the bounded C settings sync body and expose its version children."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-settings-sync-handler'
PRIOR = BASE / 'main-register-callbacks-entry/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_sync_handler_46bbb4.c'
ORACLE = HERE / 'oracle.json'
OBJECT, CURRENT, OUT = HERE / 'handler.o', HERE / 'candidate.o', HERE / 'receipt.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def undefined(path):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle['status'] == 'PASS_MAIN_SETTINGS_SYNC_HANDLER_BOUNDED_STOCK_MATCH'
    assert oracle['cases'] == 1200 and oracle['source_sha256'] == sha(SOURCE)
    assert oracle['stock_entry'] == '0x46bbb4'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    before, after = set(undefined(PRIOR)), set(undefined(CURRENT))
    removed, added = sorted(before - after), sorted(after - before)
    assert removed == ['audio_setting_handle_command5_46bbb4']
    assert added == ['audio_settings_sync_version_only_send',
                     'audio_settings_update_left_version']
    assert len(before) == 85 and len(after) == 86
    record = {
        'status': 'PASS_MAIN_SETTINGS_SYNC_HANDLER_C_INTEGRATION',
        'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
        'handler_object': ref(OBJECT), 'source': ref(SOURCE), 'oracle': ref(ORACLE),
        'native_decomp': ref(ROOT / 'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/decomp/0046bbb4.c'),
        'unresolved_before': 85, 'unresolved_after': 86,
        'removed_imports': removed, 'new_imports': added,
        'remaining_gate': 'The full settings sync dispatcher C body matches 1200 bounded stock cases. Left-version update and version-only send are new explicit unresolved child imports; peer delivery, persistence, absolute placement and whole-image behavior remain open.',
        'source_complete': False, 'flashable': False, 'hardware_proof': False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
