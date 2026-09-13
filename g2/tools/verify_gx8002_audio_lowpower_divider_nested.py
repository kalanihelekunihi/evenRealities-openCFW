# SPDX-License-Identifier: MIT
"""Audio divider wrapper with stateful decoded clock programming dependencies."""
import json, random, subprocess
from verify_gx8002_audio_lowpower_divider import verify as wrapper
from load_gx8002_clock_context import load, ROOT
from load_gx8002_clock_decoded_helpers import load_helpers
from load_gx8002_divider_decoded_helpers import load as load_leaves
from execute_gx8002_clock_module_divider import execute
from oracle_gx8002_clock_module_divider import expected
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import sha


def verify():
    table, context = load()
    modules = {row['module']: row for row in context['modules']}
    helpers, lookup_evidence = load_helpers()
    leaves, leaf_evidence = load_leaves()
    path = ROOT/'build/gx8002-board/clock-module-divider-set-candidate.elf'
    elf = Elf32(path.read_bytes(), 'divider-set')
    report = json.loads((ROOT/'docs/research/gx8002-clock-module-divider-set-source-verification.json').read_text())
    row = report['functions'][0]
    section = next(s for s in elf.sections if s['name'] == row['section_name'])
    assert sha(elf.contents(section)) == row['compiled_sha256']
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code = decode(subprocess.check_output([pre, '-d', str(path)], text=True))
    rng = random.Random(7258)
    cases = 0
    states = []
    for index in range(128):
        state = {base+off: rng.getrandbits(32) for base in (0xa0010000, 0xa0300000)
                 for off in (0x18, 0x1c, 0x20, 0x88, 0x8c)}
        for module in (7, 8):
            ptr = modules[module]['divider']
            assert ptr
            address = 0xa0010000 + table[ptr]
            state[address] = (0 if index == 0 else 0xffffffff if index == 1 else rng.getrandbits(32))
        states.append(state)
    # Four ABI poison patterns per wrapper run. Advance a single state through
    # both calls and all repeats, including the already-zero divider fast path.
    state = {}
    model = {}
    calls = []
    def program(module, divider):
        nonlocal state, model, cases
        assert (module, divider) in ((7, 0), (8, 0))
        result = execute(code, 0x10024df8, module, divider, table,
                         lambda m: (0, helpers['lookup_runner'](m)), state, **leaves)
        want = expected(module, divider, table, modules, model)
        assert result == want
        state = result[1]
        model = want[1]
        calls.append((module, divider))
        cases += 1
    # Build once; subsequent executions reuse its authenticated machine code.
    from build_gx8002_audio_lowpower_divider_candidate import build
    candidate = build()
    for initial in states:
        state = dict(initial)
        model = dict(initial)
        calls.clear()
        evidence = wrapper(program, candidate)
        assert calls == [(7, 0), (8, 0)] * 4
        assert state == model
    return {'evidence': evidence, 'state_cases': len(states), 'decoded_divider_calls': cases,
            'dependency_elf_sha256': sha(path.read_bytes()), 'lookup': lookup_evidence,
            'leaves': leaf_evidence, 'source_admitted': False,
            'limits': ['Decoded helper private frames are marshalled; ordered MMIO traces and shared final state match the independent descriptor model. Physical clock timing remains unqualified.']}

if __name__ == '__main__':
    result = verify()
    (ROOT/'docs/research/gx8002-audio-lowpower-divider-nested.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['state_cases'], result['decoded_divider_calls'])
