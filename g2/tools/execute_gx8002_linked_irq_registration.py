# SPDX-License-Identifier: MIT
"""Execute linked IRQ registration and VIC enable in one register frame."""
import re

def execute(code, start, irq, handler=0, private=0, enable=None, memory=None, call_name="enable"):
    r = {f'r{i}': 0x98760000+i for i in range(32)}
    r.update(r0=irq & 0xffffffff, r1=handler, r2=private)
    initial = r.copy()
    pc, condition, saved, writes = start, False, None, []
    return_pc=None
    for _ in range(300):
        op, args, width = code[pc]
        p = [x.strip() for x in args.split(',')]
        following = pc + width
        if op == 'push':
            if args not in ('r15', 'r4, r15') or saved is not None: raise ValueError('unexpected save')
            saved = {x:r[x] for x in p}
        elif op=='rts' and return_pc is not None:
            if r['r15']!=return_pc:raise ValueError('Enable return address')
            following=return_pc;return_pc=None
        elif op in ('pop', 'rts'):
            if op == 'pop':
                if saved is None or set(p) != set(saved): raise ValueError('unexpected restore')
                r.update(saved)
            if any(r[f'r{i}'] != initial[f'r{i}'] for i in (*range(4,12),15)): raise ValueError('ABI mismatch')
            return writes
        elif op in ('movi', 'lrw'): r[p[0]] = int(p[1], 0)
        elif op == 'mov': r[p[0]] = r[p[1]]
        elif op == 'cmpnei': condition = r[p[0]] != int(p[1],0)
        elif op == 'zext':
            high, low = map(lambda x: int(x,0), p[2:])
            r[p[0]] = (r[p[1]] >> low) & ((1 << (high-low+1))-1)
        elif op in ('andi', 'addi', 'addu', 'lsl', 'lsli'):
            a = r[p[0] if len(p)==2 else p[1]]
            b = r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]] = (a & b if op=='andi' else a << b if op in ('lsl','lsli') else a+b) & 0xffffffff
        elif op == 'cmphsi': condition = r[p[0]] >= int(p[1],0)
        elif op in ('bt','bez'):
            if condition if op=='bt' else r[p[0]]==0: following = int(p[-1],0)
        elif op in ('str.w','st.w','ld.w'):
            m = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+|r\d+ << [23])\)', args)
            if not m: raise ValueError('unsupported memory operand')
            value, base, off = m.groups()
            offset = r[off.split()[0]] << int(off[-1]) if '<<' in off else int(off,0)
            address = (r[base]+offset)&0xffffffff
            if op == 'ld.w':
                if memory is None or address not in memory: raise ValueError('unexpected read')
                r[value] = memory[address]
                writes.append(('read',address,r[value]))
            else: writes.append((address,r[value]))
        elif op == 'bsr':
            if enable is None or int(p[0],0)!=enable: raise ValueError('unexpected call')
            if return_pc is not None:raise ValueError('Nested enable')
            return_pc=following;r['r15']=following;following=enable
        else: raise ValueError('unsupported instruction '+op)
        pc = following
    raise ValueError('execution bound exceeded')

