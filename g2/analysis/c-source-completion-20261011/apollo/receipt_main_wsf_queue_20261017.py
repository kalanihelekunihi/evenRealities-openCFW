#!/usr/bin/env python3
"""Link tracked Cordio WSF queue providers into experimental Main candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CORDIO = ROOT / 'third-party/upstream/cordio'
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-wsf-queue'
PRIOR = BASE / 'main-atts-core/candidate.o'
SOURCE = CORDIO / 'wsf/sources/targets/baremetal/wsf_queue.c'
RAW, WEAK = HERE / 'wsf_queue.o', HERE / 'wsf_queue-weak.o'
CURRENT, OUT = HERE / 'candidate.o', HERE / 'receipt.json'
COLLISIONS = ('WsfQueueCount', 'WsfQueueEnq')
RESOLVED = ('WsfQueueDeq', 'WsfQueueInsert', 'WsfQueueRemove')


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
    dirs = [ROOT / 'g2/components/audio/vendor_compat', CORDIO / 'wsf/include']
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
    assert removed == sorted(RESOLVED) and not added
    assert len(prior) == 100 and len(after) == 97
    record = {'status': 'PASS_MAIN_WSF_QUEUE_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SOURCE), 'cordio_commit': '3656312d6b73e2a2c1c8b33ee0385bc199dd97e6',
              'prior_provider_precedence': list(COLLISIONS),
              'unresolved_before': 100, 'unresolved_after': 97,
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'Three queue imports resolve to tracked Cordio queue source; prior Count/Enq providers retain precedence. Vendor FreeRTOS queue variant and stock behavioral equivalence remain unverified, as do whole-image gates.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()
