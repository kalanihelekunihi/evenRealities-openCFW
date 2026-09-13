# SPDX-License-Identifier: MIT
"""Require initializer's fixed external bindings to have registered source owners."""
import json
import re
from build_gx8002_clock_init_pointer_candidate import BINDINGS, ROOT, sha
from build_transparent_image import Elf32


def verify():
    registry = (ROOT / 'tools/build_gx8002_source_candidate.py').read_text()
    owners = {}
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'", registry))):
        path = ROOT / 'docs/research' / name
        if not path.exists():continue
        report = json.loads(path.read_text())
        for row in report.get('functions', [report]):
            for occurrence in row.get('stock_occurrences', row.get('exact_stock_occurrences', [])):
                offset = occurrence.get('package_offset')
                region = occurrence.get('region', '')
                if offset is None:continue
                if 'dram' in region:delta = 0x2000dfec
                elif 'sram' in region:delta = 0x1000dfec
                elif 'xip' in region:delta = 0x101f6a74
                else:continue
                owners.setdefault(offset+delta, []).append({'report': name, 'symbol': row.get('symbol'),
                    'report_sha256': sha(path.read_bytes()), 'compiled_bytes': row.get('compiled_bytes')})
    result = {}
    for symbol, address in BINDINGS.items():
        if symbol == 's_clk_mod_gate':continue
        matches = owners.get(address, [])
        if len(matches) != 1:raise ValueError(('Missing or ambiguous source entry owner', symbol, hex(address), matches))
        result[symbol] = {'address': address, **matches[0]}
    state_report = json.loads((ROOT / 'docs/research/gx8002-clock-switch-1m-source-verification.json').read_text())
    state = state_report['runtime_state']
    elf = Elf32((ROOT / 'build/gx8002-board/clock-switch-1m-candidate.elf').read_bytes(), 'state owner')
    section = next(s for s in elf.sections if s['name'] == state['section'])
    assert section['type'] == 8 and section['address'] == state['address'] == BINDINGS['s_clk_mod_gate']
    assert section['size'] == state['bytes'] == 4
    assert state['clear_interval'][0] <= section['address'] < section['address']+4 <= state['clear_interval'][1]
    return {'bindings': result, 'saved_gate_state': state,
            'limits': ['Source ownership/entry-address audit; artifact hashes and executable semantics checked separately.',
                       'Saved-gate NOBITS section and recorded clear interval checked against its admitted owner; startup clear execution qualified separately.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'docs/research/gx8002-clock-init-bindings.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(report['bindings']))
