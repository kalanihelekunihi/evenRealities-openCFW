#!/usr/bin/env python3
"""Integrate both stock-matched settings version children into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-settings-version-children'
PRIOR = BASE / 'main-settings-sync-handler/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_version_sync_children_20261017.c'
VERSION = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_version_text.c'
ORACLE = HERE / 'oracle.json'
OBJECT, CURRENT, OUT = HERE / 'children.o', HERE / 'candidate.o', HERE / 'receipt.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def undefined(path):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle['status'] == 'PASS_MAIN_SETTINGS_VERSION_CHILDREN_BOUNDED_STOCK_MATCH'
    assert oracle['cases'] == 60
    assert oracle['source_sha256'] == sha(SOURCE)
    assert oracle['version_source_sha256'] == sha(VERSION)
    assert oracle['stock_entries'] == {'update': '0x46baec', 'send': '0x46b988'}
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    before, after = set(undefined(PRIOR)), set(undefined(CURRENT))
    removed, added = sorted(before - after), sorted(after - before)
    assert removed == ['audio_settings_sync_version_only_send',
                       'audio_settings_update_left_version'] and not added
    assert len(before) == 86 and len(after) == 84
    record = {
        'status': 'PASS_MAIN_SETTINGS_VERSION_CHILDREN_C_INTEGRATION',
        'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
        'children_object': ref(OBJECT), 'source': ref(SOURCE),
        'version_source': ref(VERSION), 'oracle': ref(ORACLE),
        'native_decomp_update': ref(ROOT / 'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/decomp/0046baec.c'),
        'native_decomp_send': ref(ROOT / 'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/decomp/0046b988.c'),
        'unresolved_before': 86, 'unresolved_after': 84,
        'removed_imports': removed, 'new_imports': added,
        'remaining_gate': 'Both version child bodies match 60 bounded stock cases and resolve the dispatcher imports. Peer transport, status notification, logging children, absolute placement and whole-image behavior remain gated.',
        'source_complete': False, 'flashable': False, 'hardware_proof': False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
