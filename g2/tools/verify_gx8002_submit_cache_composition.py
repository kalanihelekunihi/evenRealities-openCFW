#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded publication/cache composition with ordered MMIO in shared trace."""
import hashlib
import json
from itertools import product
import verify_gx8002_snpu_submit_task as submit
import verify_gx8002_snpu_task_cmd_cache_flush as wrapper
import verify_gx8002_dcache_clean_range as clean

def expected(case):
    """Expand independently modeled cache boundaries into expected MMIO."""
    trace, words = submit.expected(case)
    wanted = []
    for event in trace:
        if event[0] == 'flush_descriptor':
            writes = clean.expected(event[1], 8)
            writes += clean.expected((event[1] + 16) & clean.MASK, 108)
            wanted.extend(('mmio', *item) for item in writes)
        elif event[0] == 'clean_range':
            wanted.extend(('mmio', *item) for item in clean.expected(event[1], event[2]))
        wanted.append(event)
    return wanted, words


def composed(submit_program, wrapper_program, clean_program, case,
             model=None, stack_top=0x2002f7fc):
    """Program tuples contain decoded code, entry PC, and relocation delta."""
    def cache_call(name, address, length, stack, trace):
        def lower(pointer, size, sp):
            code, pc = clean_program
            writes, returned = clean.execute(code, pc, pointer, size, case.seed,
                                             stack_top=sp)
            if not returned:
                raise ValueError('nested clean did not return')
            trace.extend(('mmio', *item) for item in writes)
        if name == 'clean_range':
            lower(address, length, stack)
        else:
            code, pc, delta = wrapper_program
            wrapper.execute(code, pc, delta, address, case.seed,
                            clean_call=lower, stack_top=stack)
    code, pc, delta = submit_program
    return submit.execute(code, pc, delta, case, cache_call=cache_call,
                          model=model, stack_top=stack_top)


def verify():
    submit.verify()
    wrapper.verify()
    clean.verify()
    so, sn = submit.programs()
    wo, wn = wrapper.programs()
    co, cn = clean.programs()
    submissions = ((so, submit.OFFSET, submit.DELTA), (sn, submit.ADDRESS, 0))
    wrappers = ((wo, wrapper.OFFSET, wrapper.DELTA), (wn, wrapper.ADDRESS, 0))
    cleaners = ((co, clean.OFFSET), (cn, clean.ADDRESS))
    cases = 0
    for descriptor, previous, state, completed, mutation, seed in product(
            (0x20027360, 0x20027870, 0x20029000), (0, 0x20028000),
            (0, 1, 2, clean.MASK), (0, 0x40000), (False, True),
            (0, clean.MASK, 0x12345678)):
        case = submit.Case(descriptor=descriptor, previous=previous, state=state,
                           completed=completed, mutation=mutation, seed=seed)
        wanted = expected(case)
        for a, b, c in product((0, 1), repeat=3):
            if composed(submissions[a], wrappers[b], cleaners[c], case) != wanted:
                raise ValueError('publication/cache combined trace mismatch')
            cases += 1
    names = ('verify_gx8002_submit_cache_composition.py',
             'verify_gx8002_snpu_submit_task.py',
             'model_gx8002_snpu_submit_task.py',
             'verify_gx8002_snpu_task_cmd_cache_flush.py',
             'verify_gx8002_dcache_clean_range.py')
    return {
        'cases': cases,
        'source_admitted': False,
        'verifier_hashes': {
            name: hashlib.sha256((submit.ROOT / 'tools' / name).read_bytes()).hexdigest()
            for name in names
        },
        'limits': [
            'Eight stock/source combinations. Cache loops execute at nested SP; '
            'MMIO ordering checked alongside link writes. NPU register helpers '
            'remain modeled, and volatile memory is not a physical cache '
            'simulation. Caller clobbers conservative.'
        ],
    }


if __name__ == '__main__':
    report = verify()
    (submit.ROOT / 'docs/research/gx8002-submit-cache-composition.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print(report['cases'])
