#!/usr/bin/env python3
"""Link tracked Cordio ATT client supported features into Main candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CORDIO = ROOT / 'third-party/upstream/cordio'
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-atts-csf'
PRIOR = BASE / 'main-att-uuid/candidate.o'
SOURCE = CORDIO / 'ble-host/sources/stack/att/atts_csf.c'
VENDOR_SHA = '44be0c2b8ae1bac41a9fa6c5ba43041caed72573cd62e8dde7602edac81608d5'
OBJECT, RENAMED = HERE / 'atts_csf.o', HERE / 'atts_csf-namespaced.o'
CURRENT, OUT = HERE / 'candidate.o', HERE / 'receipt.json'


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
    upstream = SOURCE.read_text()
    assert hashlib.sha256(upstream.replace('connId      Connection handle.',
                                           'handle      Connection handle.').encode()).hexdigest() == VENDOR_SHA
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
                    *flags, '-c', str(SOURCE), '-o', str(OBJECT)], check=True)
    collisions = ['attsCsfSetHashUpdateStatus', 'attsCsfGetHashUpdateStatus']
    assert set(collisions).issubset(symbols(PRIOR, '--defined-only'))
    assert set(collisions).issubset(symbols(OBJECT, '--defined-only'))
    subprocess.run(['arm-none-eabi-objcopy', *[
        f'--redefine-sym={name}=g2_cordio_csf_{name}' for name in collisions],
        str(OBJECT), str(RENAMED)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(RENAMED),
                    '-o', str(CURRENT)], check=True)
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert removed == ['AttsCsfGetClientChangeAwareState', 'AttsCsfGetFeatures',
                       'AttsCsfSetClientChangeAwareState', 'attsCsfIsClientChangeAware']
    assert not added
    assert len(prior) == 113 and len(after) == 109
    record = {'status': 'PASS_MAIN_ATTS_CSF_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SOURCE), 'vendor_source_sha256': VENDOR_SHA,
              'compat_header': ref(ROOT / 'g2/components/audio/vendor_compat/string.h'),
              'collision_renames': collisions,
              'vendor_difference': 'Only the documented parameter name differs in a comment.',
              'unresolved_before': 113, 'unresolved_after': 109,
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'Four ATT CSF imports resolve to a compiled Cordio file. Its three lower-level dependencies were already in the Main frontier; stock behavior and whole-image startup/relocation remain.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
