#!/usr/bin/env python3
"""Bind authenticated ATT configuration C into experimental Main candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-att-cfg'
PRIOR = BASE / 'main-wsf-queue/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_att_cfg_200004b4_20261017.c'
OBJECT, ORACLE = HERE / 'att-cfg.o', HERE / 'oracle-receipt.json'
CURRENT, OUT = HERE / 'candidate.o', HERE / 'receipt.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle['status'] == 'PASS_MAIN_ATT_CFG_EXACT_STOCK_BYTES'
    assert oracle['source_sha256'] == sha(SOURCE) and oracle['object_sha256'] == sha(OBJECT)
    assert oracle['config_address'] == '0x78d154' and oracle['pointer_address'] == '0x200004b4'
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert removed == ['pAttCfg'] and not added
    assert len(prior) == 97 and len(after) == 96
    record = {'status': 'PASS_MAIN_ATT_CFG_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SOURCE), 'oracle': ref(ORACLE),
              'unresolved_before': 97, 'unresolved_after': 96,
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'ATT config and RAM pointer exactly match authenticated stock bytes. Whole-image relocation and remaining 96 Main imports remain.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
