#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Four decoded routines share task state and ordered cache MMIO evidence."""
import hashlib
import json
from itertools import product
import verify_gx8002_run_submit_composition as outer
import verify_gx8002_submit_cache_composition as cache


def expected(case, previous, completed):
    trace, words, result = outer.run.expected(
        case, model=outer.Shared(case, previous, completed))
    expanded = []
    for event in trace:
        writes = []
        if event[0] == 'flush_descriptor':
            writes = cache.clean.expected(event[1], 8)
            writes += cache.clean.expected((event[1] + 16) & cache.clean.MASK, 108)
        elif event[0] == 'clean_range':
            writes = cache.clean.expected(event[1], event[2])
        expanded.extend(('mmio', *item) for item in writes)
        expanded.append(event)
    return expanded, words, result


def execute(runner, publisher, wrapper, cleaner, case, previous, completed):
    shared = outer.Shared(case, previous, completed, publisher, (wrapper, cleaner))
    return outer.run.execute(*runner, case, model=shared,
                             call_hook=lambda name, arg, sp, model:
                             model.boundary(name, arg, sp))


def programs():
    modules = (outer.run, outer.submit, cache.wrapper, cache.clean)
    result = []
    for module in modules:
        old, new = module.programs()
        if module is cache.clean:
            result.append(((old, module.OFFSET), (new, module.ADDRESS)))
        else:
            result.append(((old, module.OFFSET, module.DELTA), (new, module.ADDRESS, 0)))
    return result


def verify():
    for module in (outer.run, outer.submit, cache.wrapper, cache.clean):
        module.verify()
    variants = programs()
    count = 0
    for start, end, state, previous, completed, seed in product(
            range(10), range(10), (0, 1, 2), (0, 0x20028000),
            (0, 0x40000), (0, 0xffffffff)):
        case = outer.run.Case(start=start, end=end, state=state, seed=seed)
        wanted = expected(case, previous, completed)
        for runner, publisher, wrapper, cleaner in product(*variants):
            if execute(runner, publisher, wrapper, cleaner, case, previous, completed) != wanted:
                raise ValueError('outer/publication/cache trace mismatch')
            count += 1
    names = ('verify_gx8002_run_submit_cache_composition.py',
             'verify_gx8002_run_submit_composition.py',
             'verify_gx8002_submit_cache_composition.py',
             'verify_gx8002_snpu_run_task.py', 'model_gx8002_snpu_run_task.py',
             'verify_gx8002_snpu_submit_task.py', 'model_gx8002_snpu_submit_task.py',
             'verify_gx8002_snpu_task_cmd_cache_flush.py',
             'verify_gx8002_dcache_clean_range.py')
    return {'cases': count, 'source_admitted': False,
            'verifier_hashes': {name: hashlib.sha256((outer.run.ROOT / 'tools' / name).read_bytes()).hexdigest() for name in names},
            'limits': ['All sixteen stock/source combinations. Shared task/driver memory, nested stack and ordered decoded cache MMIO. Resume state changes and NPU register helpers remain modeled. No physical cache coherence, asynchronous mutation or hardware proof.']}


if __name__ == '__main__':
    report = verify()
    (outer.run.ROOT / 'docs/research/gx8002-run-submit-cache-composition.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['cases'])
