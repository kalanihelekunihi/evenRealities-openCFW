# SPDX-License-Identifier: MIT
"""Decode loader prefix through flash probe; does not qualify full loader."""
import json,re,subprocess,itertools
from build_gx8002_kws_flash_load import build,ROOT
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
GETTERS=(0x10208bf4,0x10208bfc,0x10208c04,0x10208c08,0x10208c10)

def execute(code,entry,sizes,full=False,flash=0x20040000,statuses=(0,0),read_runner=None):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x20070000;stack={};pc=entry;calls=[];initial=r.copy();saved=None;reads=0;times=0;events=[]
    for _ in range(100):
        op,args,w=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+w
        if op=='push':
            if args not in ('r4-r9, r15','r4-r8, r15'):raise ValueError('Frame')
            saved={i:r[f'r{i}'] for i in (*range(4,10),14,15)}
            r['r14']-=28 if 'r9' in args else 24
        elif op in ('movi','mov','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op=='pop':
            if args not in ('r4-r9, r15','r4-r8, r15'):raise ValueError('Restore')
            for i in (*range(4,10 if 'r9' in args else 9),15):r[f'r{i}']=saved[i]
            r['r14']+=28 if 'r9' in args else 24
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Preserved ABI')
            return events
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op in ('bez','bnez','br'):
            if op=='br' or bool(r[p[0]])==(op=='bnez'):nxt=int(p[-1],0)
        elif op in ('addi','subi','addu','subu'):
            left=r[p[0]] if len(p)==2 else r[p[1]];right=r[p[-1]] if op in ('addu','subu') else int(p[-1],0)
            r[p[0]]=(left-right if op in ('subi','subu') else left+right)&MASK
        elif op in ('lsli','rotli'):
            v=r[p[1]];n=int(p[2],0);r[p[0]]=((v<<n)|(v>>(32-n) if op=='rotli' else 0))&MASK
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)&MASK
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))&MASK
        elif op=='bhsz':
            if r[p[0]]<0x80000000:nxt=int(p[1],0)
        elif op in ('st.w','ld.w'):
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups()
            if base!='r14':raise ValueError('Nonstack prefix write')
            offset=int(offset,0)
            expected_sp=initial['r14']-(60 if entry==0x1023c else 56)
            if r['r14']!=expected_sp or offset not in range(0,32,4):raise ValueError('Task stack bounds')
            if op=='st.w':stack[offset]=r[reg]
            else:r[reg]=stack[offset]
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0x1023c else 0))&MASK
            if target==0x1002475c:
                if tuple(r[f'r{i}'] for i in range(4))!=(0,0,6144000,2048):raise ValueError('Probe args')
                if not full:return stack,calls
                events.append(('probe',flash));value=flash
            elif target in GETTERS:value=sizes[GETTERS.index(target)]
            elif target==0x10025930:
                value=0xfffffff0 if times==0 else 0x20;times+=1
            elif target==0x100247b8:
                events.append(('read',*(r[f'r{i}'] for i in range(4))));value=read_runner(tuple(r[f'r{i}'] for i in range(4)),statuses[reads]) if read_runner else statuses[reads];reads+=1
            elif target==0x10206c24:
                events.append(('print',r['r0'],r['r1'] if r['r0']==0x1020adde else None));value=123
            elif target==0x10208c14:
                if r['r0']!=r['r14']:raise ValueError('Task pointer')
                events.append(('publish',tuple(stack.get(i,'unset') for i in range(0,32,4))));value=0
            else:raise ValueError('Unexpected prefix call')
            calls.append(target)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xab000000+i
            r['r0']=value
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')
