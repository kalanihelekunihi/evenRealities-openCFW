#!/usr/bin/env python3
"""Bind provisional C backing for the observed UART sync config prefix."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-uart-sync-storage'
PRIOR = BASE / 'main-ble-whitelist-storage/candidate.o'
SRC = ROOT / 'g2/components/audio/uart_thread_source_candidate/sync_uart_config_storage_20261017.c'
HEADER = SRC.with_name('sync_uart_config_contract.h')
PREFIX = BASE / 'uart-sync-config-contract/receipt.json'
OBJECT, CURRENT, OUT = HERE / 'storage.o', HERE / 'candidate.o', HERE / 'receipt.json'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}
def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', option, str(path)], text=True).splitlines() if line.strip()})

def main():
    HERE.mkdir(parents=True, exist_ok=True)
    prefix = json.loads(PREFIX.read_text())
    assert prefix['status'] == 'PASS_MAIN_UART_SYNC_CONFIG_PREFIX_C'
    assert prefix['header']['sha256'] == sha(HEADER)
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-ffreestanding',
                    '-fno-builtin', '-c', str(SRC), '-o', str(OBJECT)], check=True)
    rows = subprocess.check_output(['arm-none-eabi-nm', '-S', str(OBJECT)], text=True).splitlines()
    matches = [row.split() for row in rows if row.endswith(' g2_uart_sync_buffer')]
    assert len(matches) == 1 and int(matches[0][1], 16) == 16 and matches[0][2] == 'B'
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT), '-o', str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, '-u'), symbols(CURRENT, '-u')
    removed, added = sorted(set(prior)-set(current)), sorted(set(current)-set(prior))
    assert removed == ['g2_uart_sync_buffer'] and added == []
    assert len(prior) == 97 and len(current) == 96
    record = {'status': 'PASS_MAIN_UART_SYNC_STORAGE_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SRC), 'header': ref(HEADER), 'prefix_receipt': ref(PREFIX),
              'provisional_storage_bytes': 16, 'observed_prefix_bytes': 13,
              'unresolved_before': 97, 'unresolved_after': 96,
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'C RAM backing supplies a 16-byte provisional object for the 13-byte observed UART config prefix. Stock object extent, initialization bytes and placement at 0x20000d9c remain unknown. The earlier Main driver/reset objects have not been rebound to their refined sources.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(current), sha(OUT))

if __name__ == '__main__': main()
