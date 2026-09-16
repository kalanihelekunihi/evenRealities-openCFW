#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute stock and source setup against independent transaction expectations."""
import json
import hashlib
import shutil
import re
import subprocess
from itertools import product
from pathlib import Path
from verify_gx8002_logging import check_paths
from analyze_gx8002_dw_spi_setup import analyze
from build_gx8002_backup_dw_spi_setup import build, ROOT, IMAGE_SHA, sha, Elf32
from model_gx8002_backup_dw_spi_setup import Case, expected, DEVICE, FIXED_STATE, OTHER_STATE, MASK
from verify_gx8002_memcpy_source import decode

ADDRESS = 0x10008538


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
        elif op in ('movi','lrw','movih'):
            r[p[0]] = (int(p[1],0)<<(16 if op=='movih' else 0))&MASK
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
            if int(args,0)!=0x10003cf0 or r['r0']!=14:
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
    candidate=build();assert candidate['fits']
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x40e78','--stop-address=0x40eec',str(path)],text=True));stock={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        stock[pc+delta]=(op,args,width)
    source=decode((ROOT/'build/gx8002-backup-dw-spi-setup/dw-spi-setup-candidate.disassembly.txt').read_text());count=0
    for bits,speed,state,owner,clock,format,mode,changed in product((0,8,255),(0,1,25,10000000,MASK),(0,OTHER_STATE),(0,DEVICE),(0,1,100,101,100000000,MASK),(0,1,2,255),(0,3,0xffff),(None,1,20,MASK)):
        case=Case(bits,speed,state,owner,clock,format,mode,changed);want=expected(case)
        assert execute(stock,case)==want and execute(source,case)==want,case
        count+=1
    report={'candidate':candidate,'decoded_cases':count,'source_admitted':False,'limits':['Clock return and speed mutation modeled; valid distinct storage and nonzero post-call speed.','Ordered accesses and ABI checked; physical divider behavior and state allocation remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-dw-spi-setup-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['decoded_cases'])
