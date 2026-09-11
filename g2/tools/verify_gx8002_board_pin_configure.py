# SPDX-License-Identifier: MIT
"""Finite decoded board pin guard comparison; helpers remain explicit models."""
import json
import re
import subprocess
from itertools import product
from build_gx8002_board_pin_configure_candidate import ROOT, build
from verify_gx8002_memcpy_source import decode
MASK = 0xffffffff
ADDRESS = 0x102067dc


def expected(pin, function, initialized, check_result):
    trace = [('read', 0x20027b4c, initialized)]
    if initialized == 0:
        trace.append(('check', pin, int(pin != 2)))
        if check_result:
            return trace + [('printf', 0x1020ad4a, pin)], MASK
    return trace + [('set', pin, function)], 0


def execute(code, entry, pin, function, initialized, check_result, set_result, printf_result, check_hook=None, set_hook=None, printf_hook=None):
    r = {f'r{i}': (0x91234567+i*0x1020304)&MASK for i in range(32)}
    r.update(r0=pin, r1=function, r14=0x2002f7fc)
    initial = r.copy()
    saved = None
    pc = entry
    condition = False
    trace = []
    for _ in range(60):
        op, args, width = code[pc]
        p = [x.strip() for x in args.split(',')]
        nxt = pc + width
        if op == 'push':
            if args != 'r4-r5, r15' or saved is not None:
                raise ValueError('Pin guard frame')
            saved = [r[x] for x in ('r4','r5','r15')]
            r['r14'] -= 12
        elif op == 'pop':
            if args != 'r4-r5, r15' or saved is None:
                raise ValueError('Pin guard restore')
            for name, value in zip(('r4','r5','r15'), saved):
                r[name] = value
            r['r14'] += 12
            if any(r[f'r{i}'] != initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):
                raise ValueError('Pin guard ABI')
            return trace, r['r0']
        elif op in ('lrw', 'movi'):
            r[p[0]] = int(p[1], 0)&MASK
        elif op == 'mov':
            r[p[0]] = r[p[1]]
        elif op == 'subi':
            r[p[0]] = (r[p[0]] - int(p[1],0))&MASK
        elif op == 'cmpnei':
            condition = r[p[0]] != int(p[1],0)
        elif op == 'mvc':
            r[p[0]] = int(condition)
        elif op in ('bez','bnez'):
            if (r[p[0]] == 0) == (op == 'bez'):
                nxt = int(p[1],0)
        elif op == 'br':
            nxt = int(args,0)
        elif op == 'ld.w':
            match = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:
                raise ValueError('Pin guard memory operand')
            reg, base, offset = match.groups()
            address = (r[base]+int(offset,0))&MASK
            if address != 0x20027b4c:
                raise ValueError('Pin guard state address')
            r[reg] = initialized
            trace.append(('read',address,initialized))
        elif op == 'bsr':
            target = int(args,0)
            if entry == 0xfd68:
                target = (target + 0x101f6a74)&MASK
            helpers = {0x102065b8: ('check',check_result),
                       0x102065dc: ('set',set_result),
                       0x10206c24: ('printf',printf_result)}
            if target not in helpers:
                raise ValueError('Pin guard helper target')
            name, value = helpers[target]
            trace.append((name,r['r0'],r['r1']))
            hook = check_hook if name == 'check' else set_hook if name == 'set' else printf_hook
            if hook is not None:
                value = hook(r['r0'],r['r1'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):
                r[f'r{i}'] = (0xa5721368+i*0x113)&MASK
            r['r0'] = value
        else:
            raise ValueError('Unhandled pin guard instruction '+op)
        pc = nxt
    raise ValueError('Pin guard execution bound')


def programs():
    out = ROOT/'build/gx8002-board'
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old = decode(subprocess.check_output([pre,'-D','--start-address=0xfd68',
        '--stop-address=0xfda8',str(out/'padmux-get-stock.elf')],text=True))
    new = decode((out/'board-pin-configure-candidate.disassembly.txt').read_text())
    return old, new


def verify():
    candidate = build()
    old, new = programs()
    count = 0
    for case in product((0,1,2,3,31,32,33,0x7fffffff,0x80000000,MASK),
                        (0,1,3,15,255,MASK), (0,1,2,0x80000000,MASK),
                        (0,1,MASK), (0,1,MASK), (0,37,MASK)):
        want = expected(*case[:4])
        if execute(old,0xfd68,*case) != want or execute(new,ADDRESS,*case) != want:
            raise ValueError('Pin guard decoded mismatch: '+repr(case))
        count += 1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,
            'hardware_qualified':False,'limits':['Finite helper-return models and caller clobbers; separate modeled stack frame. Helper bodies, initialization lifecycle and concurrency remain unqualified.']}


if __name__ == '__main__':
    report = verify()
    (ROOT/'docs/research/gx8002-board-pin-configure-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded board pin guard cases:',report['decoded_cases'])
