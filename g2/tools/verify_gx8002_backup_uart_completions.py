# SPDX-License-Identifier: MIT
"""Decoded backup completion traces with explicitly modeled helper identities."""
import json
import subprocess
from itertools import product
from build_gx8002_backup_uart_completions import build, ROOT
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_transmit_complete import execute as transmit
from verify_gx8002_uart_receive_complete import execute as receive


def helpers(code, mapping):
    result = dict(code)
    for pc, (op, args, width) in code.items():
        if op == 'bsr':
            target = int(args, 0)
            assert target in mapping, 'Unexpected backup callee'
            result[pc] = (op, hex(mapping[target]), width)
    return result


def verify():
    candidate = build()
    runtime = lambda offset: offset - 0x3b940 + 0x10003000
    counts = {}
    d = 0x10018000  # Synthetic descriptor, not a claimed backup allocation.
    for row, kind, execute, target, identity in (
        (candidate['functions'][0], 'transmit', transmit, 0x3cec4, 0x10203598),
        (candidate['functions'][1], 'receive', receive, 0x3d850, 0x100256c0),
    ):
        offset = row['package_offset']
        old = decode(subprocess.check_output([
            str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump'), '-D',
            '--start-address=' + hex(offset),
            '--stop-address=' + hex(offset + row['stock_envelope_bytes']),
            str(ROOT / 'build/gx8002-board/padmux-get-stock.elf')], text=True))
        new = decode((ROOT / ('build/gx8002-backup-uart-completions/' + kind + '.disassembly.txt')).read_text())
        old = helpers(old, {0x3d5bc: 0x10203b38, target: identity})
        new = helpers(new, {runtime(0x3d5bc): 0x10203b38, runtime(target): identity})
        values = [(0, 1, 0xffffffff), (0, 1)]
        if kind == 'receive':
            values += [(0x10019000, 0xfffffff0), (0, 77, 0xffffffff)]
        values += [(0x10004000, 0x10004100), (0, 0x12345678), (False, True)]
        count = 0
        for args in product(*values):
            a = execute(old, offset, *args, descriptor=d)
            b = execute(new, row['runtime_address'], *args, descriptor=d)
            assert a == b
            if kind == 'transmit':
                channel, port, callback, private, mutate = args
                if mutate:
                    port, callback, private = 1, 0x10208098, 0xabcdef01
                wanted = [('read', d+124, channel), ('release', channel),
                          ('write', d+124, 0xffffffff), ('read', d, port), ('flush', port),
                          ('read', d+108, callback), ('read', d+112, private),
                          ('read', d, port), ('callback', callback, port, private)]
            else:
                channel, port, buffer, length, callback, private, mutate = args
                if mutate:
                    buffer, length, port, callback, private = 0x20060000, 128, 1, 0x10208098, 0xabcdef01
                wanted = [('read', d+104, channel), ('release', channel),
                          ('write', d+104, 0xffffffff), ('read', d+100, length),
                          ('read', d+96, buffer), ('cache', buffer, length),
                          ('read', d+88, callback), ('read', d+92, private),
                          ('read', d, port), ('callback', callback, port, private)]
            assert a[0] == wanted
            count += 1
        counts[kind] = count
    return {'candidate': candidate, 'decoded_cases': counts, 'source_admitted': False,
            'limits': ['Helpers are modeled by identity with caller clobbers and descriptor mutations, not executed.',
                       'Synthetic descriptor and callback addresses do not establish registration or placement.',
                       'No hardware qualification or receive tail admission.']}


if __name__ == '__main__':
    result = verify()
    (ROOT / 'docs/research/gx8002-backup-uart-completions-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['decoded_cases'])
