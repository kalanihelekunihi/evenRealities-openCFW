#!/usr/bin/env python3
"""Bind provisional ANCC whitelist RAM backing to the Main C candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-ble-whitelist-storage'
PRIOR = BASE / 'main-ble-atts-ind-conn/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_whitelist_info_storage_20261017.c'
ORACLE = ROOT / 'g2/analysis/c-source-completion-20261011/peripherals/verify_ble_ancc_whitelist_native.py'
OBJECT, CURRENT, OUT = HERE / 'storage.o', HERE / 'candidate.o', HERE / 'receipt.json'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}
def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', option, str(path)], text=True).splitlines() if line.strip()})

def main():
    HERE.mkdir(parents=True, exist_ok=True)
    result = subprocess.check_output(['/tmp/opencfw-oracle-venv/bin/python', str(ORACLE)], text=True).strip()
    assert result == 'PASS_BLE_ANCC_WHITELIST_NATIVE 35'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-ffreestanding',
                    '-fno-builtin', '-c', str(SOURCE), '-o', str(OBJECT)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT), '-o', str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, '-u'), symbols(CURRENT, '-u')
    removed, added = sorted(set(prior)-set(current)), sorted(set(current)-set(prior))
    assert removed == ['audio_ble_whitelist_info'] and added == []
    assert len(prior) == 98 and len(current) == 97
    assert set(removed).issubset(symbols(CURRENT, '--defined-only'))
    record = {'status': 'PASS_MAIN_BLE_WHITELIST_RAM_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SOURCE), 'native_oracle_source': ref(ORACLE),
              'native_oracle_result': result, 'unresolved_before': 98,
              'unresolved_after': 97, 'removed_imports': removed,
              'new_imports': added, 'new_providers': removed,
              'remaining_gate': 'Whitelist C storage provides the first 0x100 RAM bytes used by the 35-case native oracle. Stock capacity, startup initializer, and placement at 0x20054718 remain unverified; this is not a complete product data reconstruction.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(current), sha(OUT))

if __name__ == '__main__': main()
