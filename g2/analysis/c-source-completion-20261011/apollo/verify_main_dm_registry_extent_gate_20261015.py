#!/usr/bin/env python3
"""Guard the unresolved DM registry against an invalid 144-byte CCB alias."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
OBJECT = G2 / 'build/c-firmware/20261015/main-dm-conn2-actions-remaining-4b6afa/apollo-main-dm-conn2-actions-remaining-4b6afa.o'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_smp_db_init.c'
OUT = G2 / 'build/c-firmware/20261015/main-dm-registry-extent-gate/receipt.json'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    symbols = subprocess.check_output(['arm-none-eabi-readelf', '-sW', str(OBJECT)], text=True)
    defined = re.search(r'^\s*\d+:\s+\S+\s+(\d+)\s+OBJECT\s+GLOBAL\s+DEFAULT\s+(\d+)\s+audio_dm_connection_records$',
                        symbols, re.M)
    registry = re.search(r'^\s*\d+:\s+\S+\s+0\s+NOTYPE\s+GLOBAL\s+DEFAULT\s+UND\s+audio_ble_dm_connection_registry$',
                         symbols, re.M)
    if defined is None or int(defined.group(1)) != 144 or registry is None:
        raise RuntimeError('DM CCB and registry symbol boundary changed')
    source = SOURCE.read_text()
    if 'audio_ble_dm_connection_registry+0x90u+' not in source:
        raise RuntimeError('SMP registry callback-offset contract changed')
    record = {
        'status': 'PASS_BOUNDED_MAIN_DM_REGISTRY_EXTENT_GATE',
        'object': str(OBJECT.relative_to(ROOT)), 'object_sha256': sha(OBJECT),
        'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
        'defined_ccb_symbol': 'audio_dm_connection_records',
        'defined_ccb_bytes': 144, 'unresolved_registry_symbol': 'audio_ble_dm_connection_registry',
        'first_registry_callback_offset': 144,
        'alias_safe': False, 'source_complete': False,
        'limits': ['The current CCB object ends where the SMP initializer begins callback writes; an alias to that 144-byte object would not own those bytes.',
                   'The full dmConnCb allocation and final RAM placement must be source-owned before this import can be closed.'],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2) + '\n')
    print(record['status'], sha(OUT))

if __name__ == '__main__': main()
