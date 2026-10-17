#!/usr/bin/env python3
"""Compile tracked Cordio ATT core with existing Main providers taking precedence."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CORDIO = ROOT / 'third-party/upstream/cordio'
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-att-core'
PRIOR = BASE / 'main-atts-csf/candidate.o'
SOURCE = CORDIO / 'ble-host/sources/stack/att/att_main.c'
RAW, WEAK = HERE / 'att_main.o', HERE / 'att_main-weak.o'
CURRENT, OUT = HERE / 'candidate.o', HERE / 'receipt.json'
COLLISIONS = ('AttHandlerInit', 'attL2cDataReq', 'attMsgAlloc', 'attUuidCmp16to128')
RESOLVED = ('AttMsgFree', 'attCb', 'attCcbByConnId', 'attDecodeMsgParam',
            'attEmptyDataCback', 'attExecCallback', 'attMsgParam', 'attSetMtu')
VENDOR_NORMALIZED_SHA = '424db1e59bef38960d8d84fd1139d31ac338c7ef8334b4cbcbed97edef17fe33'


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
    normalized = '\n'.join(x.rstrip() for x in SOURCE.read_text().splitlines()) + '\n'
    assert hashlib.sha256(normalized.encode()).hexdigest() == VENDOR_NORMALIZED_SHA
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
    prior_defs, raw_defs = set(symbols(PRIOR, '--defined-only')), set(symbols(RAW, '--defined-only'))
    assert set(COLLISIONS) == prior_defs & raw_defs
    assert set(RESOLVED) == set(symbols(PRIOR, '-u')) & raw_defs
    subprocess.run(['arm-none-eabi-objcopy', *[f'--weaken-symbol={name}' for name in COLLISIONS],
                    str(RAW), str(WEAK)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(WEAK),
                    '-o', str(CURRENT)], check=True)
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert removed == sorted(RESOLVED)
    assert not added
    assert len(prior) == 109 and len(after) == 101
    assert set(COLLISIONS).issubset(symbols(CURRENT, '--defined-only'))
    record = {'status': 'PASS_MAIN_ATT_CORE_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SOURCE),
              'vendor_normalized_sha256': VENDOR_NORMALIZED_SHA,
              'prior_provider_precedence': list(COLLISIONS),
              'unresolved_before': len(prior), 'unresolved_after': len(after),
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'Eight ATT core imports resolve to tracked Cordio source, with four prior Main providers retaining precedence. Lower-level imports were already present in the frontier; stock ABI/behavior and whole-image gates remain.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
