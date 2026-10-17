#!/usr/bin/env python3
"""Bind the existing C callback registration body to its startup import."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-register-callbacks-entry'
PRIOR = BASE / 'main-clock-mux-entry/candidate.o'
SOURCE = ROOT / 'g2/components/audio/platform_callbacks_offline/stock_register_callbacks_entry.c'
BODY = ROOT / 'g2/components/audio/platform_callbacks_offline/callbacks.c'
ORACLE = HERE / 'entry-oracle.json'
OBJECT, CURRENT, OUT = HERE / 'adapter.o', HERE / 'candidate.o', HERE / 'receipt.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle['status'] == 'PASS_MAIN_REGISTER_CALLBACKS_ENTRY_STOCK_MATCH'
    assert oracle['cases'] == 168
    assert oracle['entry_source_sha256'] == sha(SOURCE)
    assert oracle['body_source_sha256'] == sha(BODY)
    assert oracle['stock_entry'] == '0x480434'
    assert 'audio_platform_callbacks_initialize' in symbols(PRIOR, '-g')
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    assert 'audio_platform_callbacks_initialize' in symbols(OBJECT, '-u')
    assert 'stock_register_callbacks' in symbols(OBJECT, '-g')
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    before, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(before - after), sorted(after - before)
    assert removed == ['stock_register_callbacks'] and not added
    assert len(before) == 86 and len(after) == 85
    record = {
        'status': 'PASS_MAIN_REGISTER_CALLBACKS_ENTRY_C_INTEGRATION',
        'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
        'adapter_object': ref(OBJECT), 'adapter_source': ref(SOURCE),
        'body_source': ref(BODY), 'entry_oracle': ref(ORACLE),
        'unresolved_before': 86, 'unresolved_after': 85,
        'removed_imports': removed, 'new_imports': added,
        'remaining_gate': 'The C callback registration table/flags match 168 bounded stock cases and the adapter binds its startup name. Selected function-pointer targets remain stock addresses; their complete C bodies, absolute placement, startup composition and device behavior remain open.',
        'source_complete': False, 'flashable': False, 'hardware_proof': False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
