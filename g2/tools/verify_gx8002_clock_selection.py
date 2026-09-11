# SPDX-License-Identifier: MIT
"""Decoded clock-source selection, including changing volatile read values."""
import json
import re
import subprocess
from itertools import product
from verify_gx8002_clock_dto_slice import ROOT, link, build_getter, programs, decode
MASK = 0xffffffff
SP = 0x2002f700
SEL = 0xa0300088
SOURCE = 0xa001008c


def expected(module, offset, source, values):
    trace = [(SOURCE, source)]
    iterator = iter(values)
    def read():
        value = next(iterator)
        trace.append((SEL, value))
        return value
    if module in (0, 1, 6, 9) and (read() >> (offset + 1)) & 1:
        return trace, 'divider', 32000
    if not ((read() >> offset) & 1):
        value = 1024000 if source & (1 << 18) else 12288000
        return trace, ('return' if module >= 10 or module in (2, 6, 9) else 'divider'), value
    if not ((read() >> offset) & 1):
        return trace, 'divider', 0
    return trace, ('pll' if source & 1 else 'dto'), (None if source & 1 else 24576000)


def execute(code, source_code, module, offset, source, values, stop_points=None):
    r = {f'r{i}': 0 for i in range(32)}
    r.update(r5=module, r14=SP)
    r['r2' if source_code else 'r1'] = offset
    pc = 0x10025258 if source_code else 0x1725a
    ends = ({0x10025246:'return', 0x100252ac:'divider', 0x100252f2:'pll', 0x10025390:'dto'} if source_code
            else {0x1737e:'return', 0x1738a:'divider', 0x172b0:'pll', 0x1732e:'dto'})
    if stop_points is not None:
        ends = stop_points
    condition = False
    trace = []
    iterator = iter(values)
    for _ in range(80):
        if pc in ends:
            kind = ends[pc]
            return trace, kind, None if kind == 'pll' else r['r4']
        op, args, width = code[pc]
        p = [x.strip() for x in args.split(',')]
        nxt = pc + width
        if op in ('movi', 'movih'):
            r[p[0]] = int(p[1], 0) << (16 if op == 'movih' else 0)
        elif op == 'ld.w':
            m = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)', args)
            if not m: raise ValueError('Selection load operand')
            reg, base, off = m.groups()
            address = (r[base] + int(off, 0)) & MASK
            if address == SP+8: r[reg] = SEL
            elif address in (SOURCE, SEL):
                r[reg] = source if address == SOURCE else next(iterator)
                trace.append((address, r[reg]))
            else: raise ValueError('Selection read address')
        elif op == 'andni':
            r[p[0]] = r[p[1]] & (~int(p[2], 0) & MASK)
        elif op in ('addi', 'andi', 'lsli', 'rotli'):
            a = r[p[1]] if len(p) == 3 else r[p[0]]
            b = int(p[-1], 0)
            r[p[0]] = (a+b if op == 'addi' else a&b if op == 'andi' else a<<b if op == 'lsli' else (a<<b)|(a>>(32-b))) & MASK
        elif op in ('lsl', 'lsr', 'and'):
            a, b = (r[p[1]], r[p[2]]) if len(p)==3 else (r[p[0]],r[p[1]])
            r[p[0]] = (a<<b if op=='lsl' else a>>b if op=='lsr' else a&b) & MASK
        elif op in ('bseti', 'bclri'):
            bit = 1 << int(p[1], 0)
            r[p[0]] = (r[p[0]]|bit) if op=='bseti' else (r[p[0]]&~bit)
        elif op in ('cmphsi', 'cmpnei'):
            condition = r[p[0]] >= int(p[1],0) if op=='cmphsi' else r[p[0]] != int(p[1],0)
        elif op in ('inct', 'incf'):
            if condition if op=='inct' else not condition:
                r[p[0]] = (r[p[1]]+int(p[2],0))&MASK
        elif op in ('bez', 'bnez'):
            if (r[p[0]]==0 if op=='bez' else r[p[0]]!=0): nxt=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or (condition if op=='bt' else not condition): nxt=int(args,0)
        else: raise ValueError('Unhandled selection instruction '+op)
        pc = nxt
    raise ValueError('Selection execution bound')


def verify():
    candidate=link();build_getter();programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x17224','--stop-address=0x173e0',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-clock-frequency/frequency-analysis.disassembly.txt').read_text())
    count=0
    for module, offset, source, bits in product(range(26), (0,4,15,30), (0,1,1<<18,(1<<18)|1), product(range(4),repeat=3)):
        values=tuple(b<<offset for b in bits)
        want=expected(module,offset,source,values)
        for code,is_source in ((old,False),(new,True)):
            actual=execute(code,is_source,module,offset,source,values)
            if actual!=want: raise ValueError(f'Selection mismatch {module,offset,source,values,is_source}: {actual} != {want}')
        count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,'limits':['Fixed-entry selection slice with valid offset 0..30; lookup, full ABI, subsequent arithmetic and hardware not qualified.']}

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-clock-selection-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded selection cases:',report['decoded_cases'])
