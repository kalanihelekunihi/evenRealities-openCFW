#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify the byte-exact board entry's unsigned dispatch and fixed writes."""
import contextlib,io,json,re,shutil
from build_gx8002_board_candidate import build,ROOT
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths

MASK=0xffffffff

def registers(code,r):
    pc=0x10203c74;trace=[];initial=r.copy()
    for _ in range(16):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('register write syntax')
            value,base,offset=m.groups();trace.append(['write',(r[base]+int(offset,0))&MASK,r[value]])
        elif op=='rts':
            if any(r[k]!=v for k,v in initial.items() if k not in ('r2','r3')):raise ValueError('register helper ABI')
            return trace
        else:raise ValueError('unknown register instruction')
        pc+=width
    raise ValueError('register helper bound')

def execute(code,reason,seed=0,resume_result=0):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc
    initial=r.copy();saved=None;pc=0x10025cbc;trace=[];carry=None
    for _ in range(32):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];next_pc=pc+width
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('board frame')
            saved=r['r15'];r['r14']-=4
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-4:raise ValueError('call frame')
            target=int(args,0);trace.append(['call',target])
            if target==0x10203c74:trace.extend(registers(code,r))
            elif target in (0x10024940,0x100245f0):
                for i in (0,1,2,3,12,13,15):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
                r['r0']=reason if target==0x10024940 else resume_result
            else:raise ValueError('unknown board helper')
        elif op=='cmphsi':carry=r[p[0]]>=int(p[1],0)
        elif op=='bf':
            if carry is None:raise ValueError('undefined condition')
            if not carry:next_pc=int(args,0)
        elif op=='pop':
            if args!='r15' or saved is None or r['r14']!=initial['r14']-4:raise ValueError('return frame')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,32))):raise ValueError('board ABI')
            return trace
        else:raise ValueError('unknown board instruction')
        pc=next_pc
    raise ValueError('board execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    if not all(row['fits'] and row['byte_exact'] for row in evidence['functions']):raise ValueError('board code changed from authenticated stock')
    code=decode((ROOT/'build/gx8002-board/board.disassembly.txt').read_text());cases=0
    for reason in sorted({0,1,2,3,0x7fffffff,0x80000000,0xffffffff,*((i*0x9e3779b9)&MASK for i in range(256))}):
     for seed in (0,0xffffffff):
      for result in (0,0xffffffff,0x20026504):
        expected=[['call',0x10024940]]
        if reason>=2:expected.append(['call',0x100245f0])
        expected.append(['call',0x10203c74]);expected.extend([['write',a,0x59] for a in (0xa0005040,0xa0005044,0xa0005048,0xa000504c)])
        if execute(code,reason,seed,result)!=expected:raise ValueError('board effects')
        cases+=1
    functions=[]
    for row in evidence['functions']:
        functions.append({'symbol':row['symbol'],'section_name':row['section'],'compiled_bytes':row['compiled_bytes'],
          'compiled_sha256':row['compiled_sha256'],'stock_occurrences':[{'symbol':row['symbol'],
          'package_offset':row['package_offset'],'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],
          'region':'image_a_xip_text' if row['section']=='.registers' else 'image_a_sram_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/board.elf',output/'board.elf')
    return {'functions':functions,'evidence':evidence,'cases':cases,'frame_bytes':4,'source_admitted':True,
            'hardware_qualified':False,'limits':['Decoded entry and register helper, byte-exact to authenticated stock. Reset/resume services modeled; physical register meanings and startup timing remain unqualified.']}
if __name__=='__main__':
    (ROOT/'docs/research/gx8002-board-initialize-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
