# SPDX-License-Identifier: MIT
"""Qualify backup entry using an explicitly rebased shared context model."""
import json
from build_gx8002_backup_irq_entry import build, ROOT
from verify_gx8002_memcpy_source import decode
from verify_gx8002_irq_compact import execute


def verify():
    evidence = build()
    raw = decode((ROOT/'build/gx8002-backup-irq-entry/entry.disassembly.txt').read_text())
    # The shared interpreter has fixed primary entry/table addresses. Translate
    # only instruction PCs, the local branch and the one table literal; all
    # register operations, stack accesses and peripheral addresses stay intact.
    delta = 0x10025574 - 0x10004880
    code = {}
    for pc, (op, args, width) in raw.items():
        if not 0x10004880 <= pc < 0x100048c6:
            continue
        parts = [p.strip() for p in args.split(',')]
        if op == 'bez':
            target = int(parts[1], 0)
            assert target == 0x100048b0
            args = parts[0] + ', ' + hex(target + delta)
        elif op == 'lrw' and int(parts[1], 0) == 0x200173a8:
            args = parts[0] + ', 0x20026ef4'
        code[pc + delta] = (op, args, width)
    cases = nested = 0
    for irq in range(32):
        for high in (0, 0x200, 0x80000000, 0xfffffe00):
            for handler in (0, 0x10004c04):
                for seed in (0, 0xffffffff, 0x12345678):
                    status = high | (irq + 32)
                    private = seed ^ 0x200174a8
                    expected = [['read', 0xe000ec00, status],
                                ['read', 0x20026ef4 + irq*8, handler]]
                    if handler:
                        expected += [['read', 0x20026ef8 + irq*8, private],
                                     ['call', handler, irq, private]]
                    result = execute(code, status, handler, private, seed)
                    assert result == {'trace': expected, 'peak_bytes': 124}
                    cases += 1
    # Each instruction reached after NIE and before NIR is an injection point.
    # Skip the null-handler branch for this sweep so every body PC is reached.
    for pc, (op, _, _) in code.items():
        if op in ('nie', 'nir'):
            continue
        result = execute(code, 42, 0x10004c04, 0x200174a8,
                         seed=0x12345678, depth=2, interrupt_pc=pc)
        assert result['peak_bytes'] >= 124
        nested += 1
    report = {'build': evidence, 'context_dispatch_cases': cases,
              'nested_injection_points_depth_two': nested,
              'address_translation': {'instruction_delta': delta,
                                      'table_from': 0x200173a8,
                                      'table_to': 0x20026ef4},
              'source_admitted': False, 'hardware_qualified': False,
              'limits': ['Exact stock bytes; shared decoded model uses explicit address rebasing.',
                         'Valid external vectors and ABI-compliant callbacks only.',
                         'Exception acceptance timing, stack capacity and physical hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-irq-entry-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    return report

if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
