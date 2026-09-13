# SPDX-License-Identifier: MIT
"""Exercise registered dispatch code with compiled mode descriptor storage."""
import json, struct, subprocess
from verify_gx8002_mode_descriptor_bindings import verify as bindings
from build_gx8002_mode_descriptors import ROOT, Elf32, sha
from compare_gx8002_mode import execute, expected, STATE, LIST, INFOS, MASK, FUNCTIONS
from verify_gx8002_memcpy_source import decode


def verify():
    ownership = bindings()
    base = {STATE: 0, STATE + 4: 0}
    paths = [ROOT / 'build/gx8002-mode-descriptors/descriptors.elf']
    idle = ownership['source_owners']['lvp_idle_mode_info'][0]
    registry = ROOT / 'build/gx8002-source-candidate'
    # The owner verifier authenticates this ELF and the descriptor's section.
    import re
    rows = re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'(gx8002-[^']+\.json)'\)",
                      (ROOT / 'tools/build_gx8002_source_candidate.py').read_text())
    artifact = next(a for kind, a, _ in rows if kind == idle['kind'])
    paths.append(registry / idle['kind'] / artifact)
    for path in paths:
        elf = Elf32(path.read_bytes(), str(path))
        for section in elf.sections:
            if section['address'] not in (LIST, *INFOS) or not section['flags'] & 2:
                continue
            data = elf.contents(section)
            assert len(data) == (8 if section['address'] == LIST else 20)
            for offset in range(0, len(data), 4):
                address = section['address'] + offset
                assert address not in base
                base[address] = struct.unpack_from('<I', data, offset)[0]
    assert len(base) == 14 and [base[LIST + i * 4] for i in range(2)] == list(INFOS)
    path = registry / 'mode/mode.elf'
    elf = Elf32(path.read_bytes(), 'mode')
    report = json.loads((ROOT / 'docs/research/gx8002-mode-verification.json').read_text())
    for row in report['functions']:
        section = next(s for s in elf.sections if s['name'] == row['section_name'])
        assert sha(elf.contents(section)) == row['compiled_sha256']
        assert section['address'] == next(f[1] for f in FUNCTIONS if f[0] == row['symbol'])
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    code = decode(subprocess.check_output([pre + 'objdump', '-d', str(path)], text=True))
    counts = {'init': 0, 'tick': 0}
    def check(kind, argument, memory, changes, seed):
        entry = FUNCTIONS[0 if kind == 'init' else 1][1]
        actual = execute(code, entry, memory, argument, changes, seed, kind)
        assert actual == expected(memory, argument, changes, kind), (kind, argument)
        counts[kind] += 1
    for argument in (0, 1, 2, 0xffff, 0x80000000, MASK):
        for first in (None, 0, 1):
            for second in (None, 0, 1):
                for seed in (0, MASK):
                    memory = dict(base); memory[STATE] = seed; memory[STATE + 4] = seed
                    check('init', argument, memory, [(first, seed), (second, seed ^ MASK)], seed)
    for index in (0, 1):
        for loop in (0, 1, 0x80000000, MASK):
            for next_index in (None, 0, 1):
                for seed in (0, MASK):
                    memory = dict(base); memory[STATE] = loop; memory[STATE + 4] = index
                    changes = [(next_index, seed)] if memory[INFOS[index] + 12] else []
                    check('tick', seed, memory, changes, seed)
    return {'bindings': ownership, 'dispatch_elf_sha256': sha(path.read_bytes()),
            'cases': counts, 'hardware_qualified': False,
            'limits': ['Executes registered compiled dispatcher against compiled list, idle and TWS descriptors. Returning callbacks are modeled with register clobbers and valid state changes; callback bodies and hardware execution are separately qualified.']}


if __name__ == '__main__':
    result = verify()
    assert json.loads(json.dumps(result)) == result
    (ROOT / 'docs/research/gx8002-mode-descriptor-dispatch.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Compiled mode descriptor dispatch:', result['cases'])
