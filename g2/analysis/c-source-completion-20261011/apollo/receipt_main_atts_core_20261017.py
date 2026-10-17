#!/usr/bin/env python3
"""Link Cordio ATT server core against the stock-word-matched procedure table."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CORDIO = ROOT / 'third-party/upstream/cordio'
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-atts-core'
PRIOR = BASE / 'main-att-core/candidate.o'
SOURCE = CORDIO / 'ble-host/sources/stack/att/atts_main.c'
ALIASED, RAW, WEAK = HERE / 'prior-tablealias.o', HERE / 'atts_main.o', HERE / 'atts_main-weak.o'
CURRENT, OUT = HERE / 'candidate.o', HERE / 'receipt.json'
COLLISIONS = ('AttsCalculateDbHash', 'AttsHashDatabaseString', 'AttsInit',
              'AttsSetAttr', 'attsCheckPendDbHashReadRsp', 'attsErrRsp',
              'attsIsHashableAttr', 'attsProcFcnTbl')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', option, str(path)], text=True).splitlines() if line.strip()})


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    assert subprocess.check_output(['git', '-C', str(CORDIO), 'rev-parse', 'HEAD'],
                                   text=True).strip() == '3656312d6b73e2a2c1c8b33ee0385bc199dd97e6'
    assert 'audio_ble_atts_proc_table_2000045c' in symbols(PRIOR, '--defined-only')
    subprocess.run(['arm-none-eabi-objcopy',
                    '--redefine-sym=audio_ble_atts_proc_table_2000045c=attsProcFcnTbl',
                    str(PRIOR), str(ALIASED)], check=True)
    dirs = [ROOT / 'g2/components/audio/vendor_compat',
            CORDIO / 'wsf/sources/port/freertos', CORDIO / 'wsf/sources',
            CORDIO / 'wsf/include', CORDIO / 'ble-host/include',
            CORDIO / 'ble-host/sources/stack/att',
            CORDIO / 'ble-profiles/sources/services']
    dirs += sorted({p.parent for p in CORDIO.rglob('*.h')})
    flags = []
    for path in dict.fromkeys(dirs):
        flags += ['-I', str(path)]
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-Wno-unused-parameter', '-ffreestanding', '-fno-builtin',
                    *flags, '-c', str(SOURCE), '-o', str(RAW)], check=True)
    prior_defs, raw_defs = set(symbols(ALIASED, '--defined-only')), set(symbols(RAW, '--defined-only'))
    assert set(COLLISIONS) == prior_defs & raw_defs
    subprocess.run(['arm-none-eabi-objcopy', *[f'--weaken-symbol={name}' for name in COLLISIONS],
                    str(RAW), str(WEAK)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-r', str(ALIASED), str(WEAK),
                    '-o', str(CURRENT)], check=True)
    assert ' D attsProcFcnTbl' in subprocess.check_output(
        ['arm-none-eabi-nm', str(CURRENT)], text=True)
    relocations = subprocess.check_output(['arm-none-eabi-readelf', '-r', str(CURRENT)], text=True)
    assert relocations.count('attsProcFcnTbl') >= 2
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert removed == ['attsCb', 'attsCcbByConnId', 'attsClearPrepWrites', 'attsDiscBusy']
    assert added == ['DmConnCheckIdle', 'WsfQueueInsert', 'WsfQueueRemove']
    assert len(prior) == 101 and len(after) == 100
    record = {'status': 'PASS_MAIN_ATTS_CORE_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SOURCE), 'cordio_commit': '3656312d6b73e2a2c1c8b33ee0385bc199dd97e6',
              'stock_table_symbol_alias': 'audio_ble_atts_proc_table_2000045c -> attsProcFcnTbl',
              'prior_provider_precedence': list(COLLISIONS),
              'table_relocation_count_min': 2,
              'unresolved_before': len(prior), 'unresolved_after': len(after),
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'Cordio ATT server core compiles and uses the stock-word-matched procedure table symbol. The tracked source differs behaviorally from the downloaded Ambiq variant; stock ABI/behavior and whole-image gates remain.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
