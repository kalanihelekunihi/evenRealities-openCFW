#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare decoded IRQ code with ordered write oracles; no hardware claim."""
import json
import re
import struct
import subprocess
from link_gx8002_irq import link
from link_gx8002_uart_console import ROOT
from analyze_gx8002_upstream_objects import IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code, start, irq, handler=0, private=0, enable=None, memory=None, call_name="enable"):
    r = {f'r{i}': 0x98760000+i for i in range(32)}
    r.update(r0=irq & 0xffffffff, r1=handler, r2=private)
    initial = r.copy()
    pc, condition, saved, writes = start, False, None, []
    for _ in range(300):
        op, args, width = code[pc]
        p = [x.strip() for x in args.split(',')]
        following = pc + width
        if op == 'push':
            if args not in ('r15', 'r4, r15') or saved is not None: raise ValueError('unexpected save')
            saved = {x:r[x] for x in p}
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
            writes.append((call_name,r['r0']))
            for i in (0,1,2,3,12,13,15): r[f'r{i}'] = 0xdead0000+i
        else: raise ValueError('unsupported instruction '+op)
        pc = following
    raise ValueError('execution bound exceeded')


def verify():
    placement = link()
    output = ROOT/'build/gx8002-irq'
    prefix = ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper = output/'stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    cases=0
    for name,offset,size in [('irq_enable',0x174c0,28),('irq_disable',0x174dc,28),('request_irq',0x17550,36)]:
        old=decode(subprocess.check_output([str(prefix)+'objdump','-D',f'--start-address={offset}',f'--stop-address={offset+size}',str(wrapper)],text=True))
        new=decode(subprocess.check_output([str(prefix)+'objdump','-d','--section=.text.open_cfw_gx8002_'+name,str(output/'irq.elf')],text=True))
        for irq in [*range(256),0x7fffffff,0x80000000,0xffffff80,0xffffffff]:
            for handler,private in ([(0,0),(0,0xffffffff),(0x10020000,0),(0x10020000,0xffffffff)] if name=='request_irq' else [(0,0)]):
                if name=='request_irq':
                    oracle=[] if irq>=32 or not handler else [(0x20026ef4+irq*8,handler),(0x20026ef8+irq*8,private),('enable',irq)]
                else:
                    oracle=[(0xe000e100+(0x80 if name=='irq_disable' else 0)+((irq>>5)&3)*4,1<<(irq&31))]
                if execute(old,offset,irq,handler,private,0x174c0)!=oracle or execute(new,offset+0x1000dfec,irq,handler,private,0x100254ac)!=oracle: raise ValueError('IRQ trace mismatch')
                cases+=1
    for name,offset,size in [('irq_restore_enabled',0x174f8,24),('irq_save_disable',0x17520,40)]:
        old=decode(subprocess.check_output([str(prefix)+'objdump','-D',f'--start-address={offset}',f'--stop-address={offset+size}',str(wrapper)],text=True))
        new=decode(subprocess.check_output([str(prefix)+'objdump','-d','--section=.text.open_cfw_gx8002_'+name,str(output/'irq.elf')],text=True))
        for a in (0,1,0x80000000,0xffffffff,0x55555555):
            for b in (0,1,0x80000000,0xffffffff,0xaaaaaaaa):
                source,dest=(0x20026eec,0xe000e100) if name=='irq_restore_enabled' else (0xe000e100,0x20026eec)
                memory={source:a,source+4:b}
                oracle=[('read',source,a),(dest,a),('read',source+4,b),(dest+4,b)]
                if name=='irq_save_disable': oracle += [('disable',i) for i in range(32)]
                if execute(old,offset,0,enable=0x174dc,memory=memory,call_name='disable')!=oracle or execute(new,offset+0x1000dfec,0,enable=0x100254c8,memory=memory,call_name='disable')!=oracle: raise ValueError('IRQ saved banks mismatch')
                cases+=1
    report={'placement':placement,'cases':cases,'source_admitted':False,'limits':['Registration enable call is modeled; VIC writes compared separately.','Finite input corpus, no concurrent mutation or hardware qualification.']}
    (ROOT/'docs/research/gx8002-irq-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(cases)
    return report

if __name__=='__main__': verify()
