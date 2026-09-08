#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Shared-state decoded outer admission/publication; resume remains modeled."""
import hashlib
import json
from itertools import product
import verify_gx8002_snpu_run_task as run
import verify_gx8002_snpu_submit_task as submit


class Shared(run.Model):
    def __init__(self, case, previous, completed, program=None, cache_programs=None):
        super().__init__(case)
        self.previous = previous
        self.completed = completed
        self.program = program
        self.cache_programs = cache_programs
        self.words[run.STATE + 0x5c0] = previous
        if previous:
            self.words[previous + 4] = 0x12345678
        if completed:
            self.words[completed + 0x20000004] = 0x34560

    def boundary(self, name, descriptor=0, stack=0x2002f7f4):
        self.trace.append((name, descriptor) if name == 'submit' else (name,))
        self.calls += 1
        if name == 'resume':
            # Qualified internal resume clears these driver words. Its decoded
            # hardware body is not part of this composition.
            for offset in (0, 0x5c0, 0x5d0):
                self.write(run.STATE + offset, 0)
            return
        case = submit.Case(descriptor=descriptor, completed=self.completed,
                           seed=self.case.seed)
        nested = submit.Model(case)
        nested.words = self.words
        nested.trace = self.trace
        if self.program is None:
            submit.expected(case, model=nested)
        elif self.cache_programs is not None:
            from verify_gx8002_submit_cache_composition import composed
            composed(self.program, *self.cache_programs, case,
                     model=nested, stack_top=stack)
        else:
            code, pc, delta = self.program
            submit.execute(code, pc, delta, case, model=nested, stack_top=stack)

    def call(self, name, *args):
        self.boundary(name, *args)


def verify():
    run.verify()
    submit.verify()
    ro, rn = run.programs()
    so, sn = submit.programs()
    runners = ((ro, run.OFFSET, run.DELTA), (rn, run.ADDRESS, 0))
    publishers = ((so, submit.OFFSET, submit.DELTA), (sn, submit.ADDRESS, 0))
    cases = 0
    for start, end, state, previous, completed, seed in product(
            range(10), range(10), (0, 1, 2), (0, 0x20028000),
            (0, 0x40000), (0, 0xffffffff)):
        case = run.Case(start=start, end=end, state=state, seed=seed)
        expected = run.expected(case, model=Shared(case, previous, completed))
        for runner, publisher in product(runners, publishers):
            model = Shared(case, previous, completed, publisher)
            def hook(name, argument, stack, shared):
                shared.boundary(name, argument, stack)
            actual = run.execute(*runner, case, model=model, call_hook=hook)
            if actual != expected:
                raise ValueError('outer/publication shared-state mismatch')
            cases += 1
    names = ('verify_gx8002_run_submit_composition.py',
             'verify_gx8002_snpu_run_task.py', 'model_gx8002_snpu_run_task.py',
             'verify_gx8002_snpu_submit_task.py', 'model_gx8002_snpu_submit_task.py')
    return {'cases': cases, 'source_admitted': False,
            'verifier_hashes': {name: hashlib.sha256((run.ROOT / 'tools' / name).read_bytes()).hexdigest() for name in names},
            'limits': ['Shared driver/task memory, ordered reads/writes and nested SP. Resume state effects and publication hardware helpers remain modeled. No asynchronous mutation or hardware execution in this composition.']}


if __name__ == '__main__':
    report = verify()
    (run.ROOT / 'docs/research/gx8002-run-submit-composition.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['cases'])
