#!/usr/bin/env python3
"""Build tracked Cordio ATTS handlers into the experimental Main C candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CORDIO = ROOT / 'third-party/upstream/cordio'
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-atts-handlers'
PRIOR = BASE / 'main-atts-proc-table/candidate.o'
OUT = HERE / 'receipt.json'
STEMS = ('atts_proc', 'atts_read', 'atts_write', 'atts_ind')
COLLISIONS = {
    'atts_proc': ('attsFindByHandle', 'attsUuidCmp'),
    'atts_read': ('attsFindUuidInRange',),
    'atts_write': (),
    'atts_ind': ('AttsIndInit',),
}
HANDLERS = {
    'attsProcMtuReq', 'attsProcFindInfoReq', 'attsProcFindTypeReq',
    'attsProcReadTypeReq', 'attsProcReadReq', 'attsProcReadBlobReq',
    'attsProcReadMultReq', 'attsProcReadGroupTypeReq', 'attsProcWrite',
    'attsProcPrepWriteReq', 'attsProcExecWriteReq', 'attsProcValueCnf',
    'attsProcReadMultiVarReq',
}


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
    paths = [ROOT / 'g2/components/audio/vendor_compat',
             CORDIO / 'wsf/sources/port/freertos', CORDIO / 'wsf/sources',
             CORDIO / 'wsf/include', CORDIO / 'ble-host/include',
             CORDIO / 'ble-host/sources/stack/att',
             CORDIO / 'ble-profiles/sources/services']
    paths += sorted({p.parent for p in CORDIO.rglob('*.h')})
    includes = []
    for path in dict.fromkeys(paths):
        includes += ['-I', str(path)]
    sources, objects = [], []
    for stem in STEMS:
        source = CORDIO / 'ble-host/sources/stack/att' / f'{stem}.c'
        raw = HERE / f'{stem}.o'
        renamed = HERE / f'{stem}-namespaced.o'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                        '-Wno-unused-parameter', '-ffreestanding', '-fno-builtin',
                        *includes, '-c', str(source), '-o', str(raw)], check=True)
        defs = set(symbols(raw, '--defined-only'))
        assert set(COLLISIONS[stem]).issubset(defs)
        subprocess.run(['arm-none-eabi-objcopy', *[
            f'--redefine-sym={name}=g2_cordio_{stem}_{name}'
            for name in COLLISIONS[stem]], str(raw), str(renamed)], check=True)
        sources.append(ref(source))
        objects.append(renamed)
    current = HERE / 'candidate.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR),
                    *map(str, objects), '-o', str(current)], check=True)
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(current, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert set(removed) == HANDLERS and len(prior) == 107
    assert HANDLERS.issubset(symbols(current, '--defined-only'))
    assert len(after) == 115, (len(after), added)
    record = {
        'status': 'PASS_MAIN_ATTS_HANDLERS_C_INTEGRATION',
        'prior_candidate': ref(PRIOR), 'candidate_object': ref(current),
        'cordio_commit': '3656312d6b73e2a2c1c8b33ee0385bc199dd97e6',
        'sources': sources, 'compat_header': ref(ROOT / 'g2/components/audio/vendor_compat/string.h'),
        'collision_renames': COLLISIONS,
        'compile_flags_exception': '-Wno-unused-parameter',
        'unresolved_before': len(prior), 'unresolved_after': len(after),
        'removed_imports': removed, 'new_imports': added,
        'remaining_gate': 'Thirteen tracked Cordio ATTS handler bodies compile and link. Their stock behavioral and ABI equivalence is not established; 115 Main imports and whole-image startup/relocation remain.',
        'source_complete': False, 'flashable': False, 'hardware_proof': False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
