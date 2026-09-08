#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded GPIO trigger registration equivalence checks."""
import json
import re
import shutil
import struct
import subprocess
from itertools import product
from build_gx8002_gpio_disable_trigger_candidate import ROOT, IMAGE, build, sha
from model_gx8002_gpio_disable_trigger import Case, Model, expected, MASK
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths

OFFSET = 0xf600
ADDRESS = 0x10206074


def execute(code, pc, case, delta=0, table=None):
    m = Model(case)
    r = {f'r{i}': (case.seed ^ i * 0x1020304) & MASK for i in range(32)}
    r['r0'],r['r1'],r['r2'],r['r3'] = case.port,case.trigger,case.callback,case.private
    r['r14'] = 0x2002f7fc
    initial = r.copy()
    saved = None
    condition = False
    for _ in range(800):
        op, args, width = code[pc]
        p = [x.strip() for x in args.split(',')]
        nxt = pc + width
        if op == 'push':
            if args != 'r4, r15' or saved is not None:
                raise ValueError('GPIO frame')
            saved = {f'r{i}': r[f'r{i}'] for i in (4, 15)}
            r['r14'] -= 8
        elif op in ('movi', 'lrw'):
            r[p[0]] = int(p[1], 0) & MASK
        elif op == 'mov':
            r[p[0]] = r[p[1]]
        elif op in ('rotli','rotl'):
            value=r[p[1]] if len(p)==3 else r[p[0]]
            shift=(r[p[-1]] if p[-1] in r else int(p[-1],0))&31
            r[p[0]]=((value<<shift)|(value>>((32-shift)&31)))&MASK
        elif op in ('lsl', 'and', 'or'):
            a = r[p[1]] if len(p) == 3 else r[p[0]]
            b = r[p[-1]]
            if op == 'lsl' and b >= 32:
                raise ValueError('GPIO shift outside qualified pin range')
            r[p[0]] = (a << b if op == 'lsl' else a | b if op == 'or' else a & b) & MASK
        elif op in ('addi','subi','addu','mult'):
            a=r[p[1]] if len(p)==3 else r[p[0]]
            b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a-b if op=='subi' else a*b if op=='mult' else a+b)&MASK
        elif op in ('str.w','ldr.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args)
            if not match:raise ValueError('GPIO indexed operand')
            reg,base,index,shift=match.groups();address=(r[base]+(r[index]<<int(shift)))&MASK
            if op=='str.w':m.write(address,r[reg])
            else:
                if table is None or address not in table:raise ValueError('GPIO table bounds')
                r[reg]=table[address]
        elif op=='jmp':nxt=(r[args]-delta)&MASK
        elif op in ('ld.w', 'st.w'):
            match = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)', args)
            if not match:
                raise ValueError('GPIO memory operand')
            reg, base, off = match.groups()
            address = (r[base] + int(off, 0)) & MASK
            if op == 'ld.w':
                r[reg] = m.read(address)
            else:
                m.write(address, r[reg])
        elif op == 'bez':
            if r[p[0]] == 0:
                nxt = int(p[1], 0)
        elif op in ('cmpnei','cmphsi'):
            condition = r[p[0]] != int(p[1],0) if op=='cmpnei' else r[p[0]]>=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'):
                nxt = int(args, 0)
        elif op == 'bsr':
            if saved is None or r['r14'] != initial['r14']-8:raise ValueError('GPIO helper frame')
            target=(int(args,0)+delta)&MASK
            if target==0x10205f24:m.call('direction',r['r0'],r['r1'])
            else:raise ValueError('GPIO helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):
                r[f'r{i}']=(case.seed ^ i*0x1234567)&MASK
        elif op == 'rts':
            if saved is not None or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('GPIO leaf ABI')
            return m.trace,m.words,r['r0']
        elif op == 'pop':
            if saved is None or args != 'r4, r15' or r['r14'] != initial['r14'] - 8:
                raise ValueError('GPIO return frame')
            r.update(saved)
            r['r14'] += 8
            if any(r[f'r{i}'] != initial[f'r{i}'] for i in (*range(4, 12), 14, 15, 16, 17)):
                raise ValueError('GPIO ABI')
            return m.trace, m.words, r['r0']
        else:
            raise ValueError('GPIO unknown instruction ' + op)
        pc = nxt
    raise ValueError('GPIO execution bound')


def programs():
    out = ROOT / 'build/gx8002-board'
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    path = out / 'gpio-disable-trigger-stock.elf'
    subprocess.run([pre + 'objcopy', '-I', 'binary', '-O', 'elf32-csky-little', '-B', 'csky', str(IMAGE), str(path)], check=True)
    data = bytearray(path.read_bytes())
    struct.pack_into('<I', data, 36, 0x21006009)
    path.write_bytes(data)
    old = decode(subprocess.check_output([pre + 'objdump', '-D', '--start-address=0xf600', '--stop-address=0xf65c', str(path)], text=True))
    new = decode((out / 'gpio-disable-trigger-candidate.disassembly.txt').read_text())
    return old, new


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    evidence = build()
    old, new = programs()
    cases=0
    for port,seed in product((*range(33),0x80000000,MASK),(0,MASK,0x12345678,*[1<<i for i in range(32)])):
        case=Case(port=port,seed=seed)
        wanted=expected(case)
        if execute(old,OFFSET,case,0x101f6a74)!=wanted or execute(new,ADDRESS,case)!=wanted:
            raise ValueError('GPIO disable trace mismatch')
        cases+=1
    if not evidence['fits']:
        raise ValueError('GPIO envelope')
    row = {key: evidence[key] for key in ('symbol', 'section_name', 'compiled_bytes', 'compiled_sha256')}
    row['stock_occurrences'] = [{'symbol': evidence['symbol'], 'package_offset': OFFSET, 'bytes': 92, 'sha256': evidence['stock_sha256'], 'region': 'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'build/gx8002-board/gpio-disable-trigger-candidate.elf', output / 'gpio-disable-trigger.elf')
    return {'functions': [row], 'evidence': evidence, 'cases': cases,
            'model_sha256': sha((ROOT / 'tools/model_gx8002_gpio_disable_trigger.py').read_bytes()),
            'shared_model_sha256': sha((ROOT / 'tools/model_gx8002_gpio_trigger.py').read_bytes()),
            'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Ordered five trigger-register clears and callback cleanup, port rejection, helper calls/clobbers and 8-byte frame. Direction helper remains modeled; no hardware proof.']}


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-gpio-disable-trigger-verification.json').write_text(json.dumps(verify(), indent=2) + '\n')
