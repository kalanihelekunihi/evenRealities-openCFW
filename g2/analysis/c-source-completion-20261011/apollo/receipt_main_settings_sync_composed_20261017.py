#!/usr/bin/env python3
"""Bind the composed dispatcher/version oracle to the current Main object."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-settings-sync-composed'
CURRENT = BASE / 'main-settings-version-children/candidate.o'
ORACLE = HERE / 'oracle.json'
DISPATCH = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_sync_handler_46bbb4.c'
CHILDREN = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_version_sync_children_20261017.c'
VERSION = ROOT / 'g2/components/audio/uart_thread_source_candidate/settings_version_text.c'
OUT = HERE / 'receipt.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle['status'] == 'PASS_MAIN_SETTINGS_SYNC_COMPOSED_STOCK_MATCH'
    assert oracle['cases'] == 2400
    assert oracle['dispatcher_source_sha256'] == sha(DISPATCH)
    assert oracle['version_children_source_sha256'] == sha(CHILDREN)
    assert oracle['version_text_source_sha256'] == sha(VERSION)
    assert oracle['stock_dispatcher_entry'] == '0x46bbb4'
    prior = json.loads((BASE / 'main-settings-version-children/receipt.json').read_text())
    assert prior['status'] == 'PASS_MAIN_SETTINGS_VERSION_CHILDREN_C_INTEGRATION'
    assert prior['candidate_object']['sha256'] == sha(CURRENT)
    assert prior['unresolved_after'] == 84
    record = {
        'status': 'PASS_MAIN_SETTINGS_SYNC_COMPOSED_C_EVIDENCE',
        'current_candidate': ref(CURRENT), 'oracle': ref(ORACLE),
        'dispatcher_source': ref(DISPATCH), 'version_children_source': ref(CHILDREN),
        'version_text_source': ref(VERSION),
        'prior_integration_receipt': ref(BASE / 'main-settings-version-children/receipt.json'),
        'composed_cases': 2400, 'unresolved_imports': 84,
        'remaining_gate': 'The dispatcher and both version children compose across 2400 stock/C cases. Lower level send, notification, logging and copy services remain controlled, and final layout and device behavior are unproven.',
        'source_complete': False, 'flashable': False, 'hardware_proof': False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], sha(OUT))


if __name__ == '__main__':
    main()
