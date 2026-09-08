#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute stock and source setup against independent transaction expectations."""
import json
import hashlib
import re
import subprocess
from itertools import product
from pathlib import Path
from analyze_gx8002_dw_spi_setup import analyze
from build_gx8002_dw_spi_setup_candidate import build, ROOT
from model_gx8002_dw_spi_setup import Case, expected, DEVICE, FIXED_STATE, OTHER_STATE, MASK
from verify_gx8002_memcpy_source import decode

ADDRESS = 0x10206190


def execute(code, case):
    memory = {}
    def put(address, value, size):
        for i in range(size):
            memory[address+i] = (value >> (8*i)) & 255
    def get(address, size):
        return sum(memory[address+i] << (8*i) for i in range(size))
    for base, length in ((DEVICE, 20), (FIXED_STATE, 16), (OTHER_STATE, 16)):
        for i in range(length):
            memory[base+i] = (i*17+93) & 255
    put(DEVICE+9, case.bits, 1)
    put(DEVICE+4, case.speed, 4)
    put(DEVICE+12, case.state, 4)
    put(DEVICE+16, case.format, 1)
    put(FIXED_STATE, case.owner, 4)
    r = {f'r{i}': (0x73917531+i*0x1020304)&MASK for i in range(32)}
    r['r0'] = DEVICE
    r['r14'] = 0x2002f7fc
    initial = r.copy()
    trace = []
    condition = False
    pc = ADDRESS
    saved = None
    for _ in range(200):
        op, args, width = code[pc]
        p = [x.strip() for x in args.split(',')]
        nxt = pc+width
        if op == 'push':
            if args != 'r4-r5, r15' or saved is not None:
                raise ValueError('Setup stack frame')
            saved = [r[x] for x in ('r4','r5','r15')]
            r['r14'] -= 12
        elif op == 'pop':
            if args != 'r4-r5, r15' or saved is None:
                raise ValueError('Setup stack return')
            for reg, value in zip(('r4','r5','r15'), saved):
                r[reg] = value
            r['r14'] += 12
            if any(r[f'r{i}'] != initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):
                raise ValueError('Setup ABI')
            return trace, r['r0']
        elif op in ('movi','lrw'):
            r[p[0]] = int(p[1],0)&MASK
        elif op == 'mov':
            r[p[0]] = r[p[1]]
        elif op.startswith('ld.') or op.startswith('st.'):
            match = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)', args)
            if not match:
                raise ValueError('Setup memory operand')
            reg, base, offset = match.groups()
            size = {'w':4, 'h':2, 'b':1}[op[-1]]
            address = (r[base]+int(offset,0))&MASK
            if op.startswith('ld'):
                r[reg] = get(address,size)
                trace.append(('read'+str(size*8),address,r[reg]))
            else:
                value = r[reg]&((1<<(size*8))-1)
                put(address,value,size)
                trace.append(('write'+str(size*8),address,value))
        elif op == 'zextb':
            r[p[0]] = r[p[1]]&255
        elif op in ('addi','subi','lsli'):
            a = r[p[1]] if len(p)==3 else r[p[0]]
            b = int(p[-1],0)
            r[p[0]] = (a+b if op=='addi' else a-b if op=='subi' else a<<b)&MASK
        elif op == 'divu':
            r[p[0]] = r[p[1]]//r[p[2]]
        elif op in ('and','or','mult'):
            a,b = r[p[0]],r[p[1]]
            r[p[0]] = (a&b if op=='and' else a|b if op=='or' else a*b)&MASK
        elif op in ('andi','andni'):
            mask = int(p[2],0)
            r[p[0]] = r[p[1]] & (mask if op=='andi' else ~mask)&MASK
        elif op in ('bclri','bseti'):
            mask = 1<<int(p[1],0)
            r[p[0]] = (r[p[0]]&~mask if op=='bclri' else r[p[0]]|mask)&MASK
        elif op == 'cmpne':
            condition = r[p[0]] != r[p[1]]
        elif op == 'inct':
            r[p[0]] = (r[p[1]]+(int(p[2],0) if condition else 0))&MASK
        elif op in ('bez','bnez'):
            if (r[p[0]]==0) == (op=='bez'):
                nxt = int(p[1],0)
        elif op in ('bf','bt','br'):
            if op=='br' or condition==(op=='bt'):
                nxt = int(args,0)
        elif op == 'bsr':
            if int(args,0)!=0x10025210 or r['r0']!=14:
                raise ValueError('Setup clock call')
            trace.append(('clock',14,case.clock))
            put(DEVICE+10,case.mode_after_call,2)
            if case.speed_after_call is not None:
                put(DEVICE+4,case.speed_after_call,4)
            for i in (0,1,2,3,12,13,15,*range(18,32)):
                r[f'r{i}'] = (0xa59137db+i*0x113)&MASK
            r['r0'] = case.clock
        else:
            raise ValueError('Unhandled setup instruction '+op)
        pc = nxt
    raise ValueError('Setup step bound')


def verify():
    attribution = analyze()
    candidate = build()
    out = ROOT/'build/gx8002-board'
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock = decode(subprocess.check_output([pre,'-d',str(out/'dw-spi-setup-oracle.elf')],text=True))
    source = decode((out/'dw-spi-setup-candidate.disassembly.txt').read_text())
    count = 0
    for bits,speed,state,owner,clock,format,mode,changed in product(
            (0,8,255),(0,1,25,10000000,MASK),(0,OTHER_STATE),(0,DEVICE),
            (0,1,100,101,100000000,MASK),(0,1,2,255),(0,3,0xffff),(None,1,20,MASK)):
        case = Case(bits,speed,state,owner,clock,format,mode,changed)
        want = expected(case)
        if execute(stock,case)!=want or execute(source,case)!=want:
            raise ValueError('Setup behavior mismatch: '+repr(case))
        count += 1
    evidence_files = ('verify_gx8002_dw_spi_setup.py', 'model_gx8002_dw_spi_setup.py',
                      'analyze_gx8002_dw_spi_setup.py', 'build_gx8002_dw_spi_setup_candidate.py')
    evidence_hashes = {name: hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest()
                       for name in evidence_files}
    return {'candidate':candidate,'attribution':attribution,'decoded_cases':count,
            'evidence_sha256':evidence_hashes,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Candidate exceeds original slot; no integration admission.',
                      'Clock helper effects modeled; valid distinct state/device storage and nonzero post-call speed required.']}

if __name__ == '__main__':
    report = verify()
    (ROOT/'docs/research/gx8002-dw-spi-setup-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded cases:',report['decoded_cases'])
