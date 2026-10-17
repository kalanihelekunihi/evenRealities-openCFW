#!/usr/bin/env python3
"""Bind the stock clock-reset call to the verified C R5 entry adapter."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-clock-mux-entry'
PRIOR = BASE / 'main-ble-slave-connection-alias/candidate.o'
SOURCE = ROOT / 'g2/components/audio/clock_reset_active_offline/stock_clock_mux_reset_entry.c'
HELPER = ROOT / 'g2/components/audio/clock_reset_active_offline/recovery.c'
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
    assert oracle['status'] == 'PASS_MAIN_CLOCK_MUX_ENTRY_R5_ADAPTER_STOCK_MATCH'
    assert oracle['cases'] == 120
    assert oracle['adapter_source_sha256'] == sha(SOURCE)
    assert oracle['helper_source_sha256'] == sha(HELPER)
    assert oracle['stock_entry'] == '0x44b158'
    assert 'clock_reset_recover' in symbols(PRIOR, '-g')
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    disassembly = subprocess.check_output(['arm-none-eabi-objdump', '-dr',
                                           str(OBJECT)], text=True)
    assert 'mov\tr0, r5' in disassembly
    assert 'R_ARM_THM_JUMP24\tclock_reset_recover' in disassembly
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    before, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(before - after), sorted(after - before)
    assert removed == ['stock_clock_mux_reset'] and not added
    assert len(before) == 87 and len(after) == 86
    record = {
        'status': 'PASS_MAIN_CLOCK_MUX_ENTRY_C_INTEGRATION',
        'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
        'adapter_object': ref(OBJECT), 'adapter_source': ref(SOURCE),
        'helper_source': ref(HELPER), 'entry_oracle': ref(ORACLE),
        'unresolved_before': 87, 'unresolved_after': 86,
        'removed_imports': removed, 'new_imports': added,
        'remaining_gate': 'Clock-reset entry and helper match 120 bounded stock cases under modeled peripheral readiness. Absolute placement, unmodeled provider behavior, startup composition and device behavior remain unproven.',
        'source_complete': False, 'flashable': False, 'hardware_proof': False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
