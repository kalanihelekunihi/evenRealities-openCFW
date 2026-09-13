# SPDX-License-Identifier: MIT
"""Check backup preservation predicate including the called status decoder."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_preserve_memory import build,ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode

def execute(code,entry,values):
    r={f'r{i}':0x76540000+i for i in range(32)};initial=dict(r)
    pc=entry;calls=[];saved=None;condition=False;trace=[]
    for _ in range(90):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r15';saved=r['r15'];r['r14']-=4
        elif op=='pop':
            assert args=='r15' and saved is not None;r['r15']=saved;r['r14']+=4
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],trace
        elif op=='bsr':calls.append(nxt);nxt=int(args,0)
        elif op=='rts':
            if calls:nxt=calls.pop()
            else:
                assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
                return r['r0'],trace
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('andi','subi','lsli'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a&b if op=='andi' else a-b if op=='subi' else a<<b)&0xffffffff
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='bt':
            if condition:nxt=int(args,0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,offset=m.groups();address=r[base]+int(offset,0)
            r[reg]=values[address];trace.append((address,r[reg]))
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('predicate bound')

def verify():
    candidate=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),str(p));assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x3c8f8','--stop-address=0x3c95a',str(p)],text=True))
    new=decode((ROOT/'build/gx8002-backup-preserve-memory/predicate.disassembly.txt').read_text());cases=0
    for flags,high,fallback,preserve,discard in product(range(16),(0,0xfffffff0),(0,1,0xffffffff),(0,1,2,0xffffffff),(0,0x12345678)):
        values={0xa0000034:flags|high,0xa001002c:fallback,0xa0010058:preserve,0xa001005c:discard}
        a=execute(old,0x3c93c,values);b=execute(new,0x10003ffc,values)
        addresses=[0xa0000034]+([0xa0010058,0xa001005c] if flags else [0xa001002c])
        assert a==b==(preserve&1 if flags else 0,[(v,values[v]) for v in addresses]);cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Register reads modeled; physical status meaning and asynchronous changes between reads not qualified.','Placement/reference gate remains separate.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-preserve-memory-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'],'cases passed')
