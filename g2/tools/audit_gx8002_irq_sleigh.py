#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Audit pinned decompiler stack definitions; not a hardware IRQ emulator."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'build/upstream-ghidra-csky-winnermicro'
COMMIT = '0daaa056e8c570ba514fc0d0226384ecf9f9df05'


def pinned(relative):
    data = subprocess.check_output(['git', '-C', str(PLUGIN), 'show', f'{COMMIT}:{relative}'])
    if (PLUGIN / relative).read_bytes() != data:
        raise ValueError('working definition differs from pinned source: ' + relative)
    return data.decode(), hashlib.sha256(data).hexdigest()


def sequence(source, instruction, operation):
    body = re.search(r':' + instruction + r'\s+is[^\{]+\{([^}]+)\}', source)
    if body is None:
        raise ValueError('missing instruction ' + instruction)
    return re.findall(operation + r'\((\w+)\);', body[1])


def roundtrip(pushes, pops):
    if set(pushes) != set(pops) or len(set(pushes)) != len(pushes):
        raise ValueError('unexpected register coverage')
    original = {name: 0x12340000 + i for i, name in enumerate(pushes)}
    stack = [original[name] for name in pushes]
    restored = {name: stack.pop() for name in pops}
    return {'push_order': pushes, 'pop_order': pops,
            'preserves_registers': restored == original,
            'mismatches': {name: {'before': original[name], 'after': restored[name]}
                           for name in pushes if original[name] != restored[name]}}


def main():
    base = 'C-SKY/data/languages/'
    macros, macro_sha = pinned(base + 'csky_v2.sinc')
    instructions, instruction_sha = pinned(base + '16b_memory.sinc')
    compact = re.sub(r'\s+', '', macros)
    for definition in ('macropush(x){sp=sp-4;*:4sp=x;}',
                       'macropop(x){x=*:4sp;sp=sp+4;}'):
        if definition not in compact:
            raise ValueError('stack macro semantics changed; re-review required')
    pairs = {}
    for save, restore in [('ipush', 'ipop'), ('nie', 'nir')]:
        pairs[save + '/' + restore] = roundtrip(sequence(instructions, save, 'push'),
                                               sequence(instructions, restore, 'pop'))
    report = {'plugin_commit': COMMIT,
              'source': 'https://github.com/taligentx/ghidra_csky_WinnerMicro',
              'file_sha256': {'csky_v2.sinc': macro_sha, '16b_memory.sinc': instruction_sha},
              'pairs': pairs, 'hardware_semantics_proven': False,
              'admitted': False,
              'limitation': 'Audits only explicit SLEIGH stack operations. Does not establish hardware order, automatic frames, stack selection, or nesting semantics.'}
    output = ROOT / 'docs/research/gx8002-irq-sleigh-audit.json'
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
