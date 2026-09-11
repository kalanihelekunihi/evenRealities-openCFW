# SPDX-License-Identifier: MIT
"""Replay the byte-identical channel lookup and its caller's byte narrowing."""
import json
import subprocess
from build_gx8002_channel_lookup_candidate import build
from analyze_gx8002_upstream_objects import ROOT
from verify_gx8002_memcpy_source import decode


def execute(code, entry, channel):
    registers = {'r0': channel & 0xffffffff, 'r3': 0xa5a5a5a5}
    pc = entry
    condition = False
    for _ in range(12):
        op, operands, width = code[pc]
        args = [a.strip() for a in operands.split(',')]
        if op == 'bez':
            if registers[args[0]] == 0:
                pc = int(args[1], 0)
                continue
        elif op == 'cmpnei': condition = registers[args[0]] != int(args[1], 0)
        elif op in ('movi', 'lrw'): registers[args[0]] = int(args[1], 0)
        elif op == 'inct':
            if condition: registers[args[0]] = (registers[args[1]] + int(args[2], 0)) & 0xffffffff
        elif op == 'br':
            pc = int(args[0], 0)
            continue
        elif op == 'rts': return registers['r0']
        else: raise ValueError('Unexpected channel lookup instruction '+op)
        pc += width
    raise ValueError('Channel lookup did not return')


def verify():
    candidate = build()
    if candidate['compiled_sha256'] != candidate['stock_sha256'] or candidate['compiled_bytes'] != 28:
        raise ValueError('Channel lookup no longer byte-identical')
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old = decode(subprocess.check_output([pre, '-D', '--start-address=0x1104c', '--stop-address=0x11068', str(ROOT/'build/gx8002-board/padmux-get-stock.elf')], text=True))
    new = decode((ROOT/'build/gx8002-board/channel-lookup-candidate.disassembly.txt').read_text())
    values = list(range(256)) + [0x3fffffff, 0x7fffffff, 0xbfffffff, 0xffffffff]
    for value in values:
        expected = {0: 0x2002e050, 1: 0x2002e1cc}.get(value, 0)
        for code, entry in ((old, 0x1104c), (new, 0x10207ac0)):
            if execute(code, entry, value) != expected: raise ValueError('Channel lookup result')
    caller = decode(subprocess.check_output([pre, '-D', '--start-address=0x11624',
        '--stop-address=0x1163c', str(ROOT/'build/gx8002-board/padmux-get-stock.elf')], text=True))
    required = {0x1162a: ('zextb', 'r9, r0'), 0x1162c: ('mov', 'r7, r0'),
                0x1162e: ('mov', 'r0, r9'), 0x11632: ('bsr', '0x1104c'),
                0x11636: ('mov', 'r4, r0'), 0x11638: ('bez', 'r0, 0x117fc')}
    for pc, instruction in required.items():
        if caller[pc][:2] != instruction:
            raise ValueError('Caller argument/rejection evidence changed at '+hex(pc))
    aliases = values[-4:]
    if any(execute(old, 0x1104c, x & 255) for x in aliases):
        raise ValueError('Wrapping sensor index passed lookup')
    return {'candidate': candidate, 'decoded_cases': 2*len(values),
            'caller_instruction_evidence': {hex(pc): list(instruction) for pc, instruction in required.items()},
            'wrapping_indices_rejected_after_byte_narrowing': aliases,
            'source_admitted': False, 'hardware_qualified': False,
            'limits': ['Lookup and caller byte-narrowing only. Rejection branch is separately visible at package 0x11638; no global exclusion of sensor writers.']}

if __name__ == '__main__':
    report = verify()
    (ROOT/'docs/research/gx8002-channel-lookup-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Channel lookup decoded cases:', report['decoded_cases'])
