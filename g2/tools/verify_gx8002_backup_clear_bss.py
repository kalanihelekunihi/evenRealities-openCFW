# SPDX-License-Identifier: MIT
"""Compare full-range decoded C BSS clearing with the authenticated stock loop."""
import json,subprocess
from build_gx8002_backup_clear_bss import build,ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_backup_dma_callback_clear import execute as stock_execute
from verify_gx8002_memcpy_source import decode

def source_execute(code,seed):
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};initial=dict(r)
    memory={a:seed for a in range(0x20017090,0x2002d79c,4)};writes=[];pc=0x10003128;condition=False
    for _ in range(120000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='bf':
            if not condition:nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op=='stbi.w':
            assert args=='r1, (r3)' and r['r3'] in memory
            memory[r['r3']]=r['r1'];writes.append(r['r3']);r['r3']+=4
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            assert writes==list(range(0x20017090,0x2002d79c,4))
            return memory
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('clear bound')

def verify():
    candidate=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),str(p));assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x3ba68','--stop-address=0x3ba80',str(p)],text=True))
    new=decode((ROOT/'build/gx8002-backup-clear-bss/clear.disassembly.txt').read_text())
    for seed in (0,1,0x98765432,0xffffffff):
        a=stock_execute(old,seed);b=source_execute(new,seed);assert a==b and all(v==0 for v in b.values())
    return {'candidate':candidate,'cases':4,'words_per_case':22979,'source_admitted':False,'limits':['Fixed recovered range and ordered word stores checked; startup condition remains separate.','Residual literal-pool placement and hardware alias/retention require separate qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-clear-bss-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'full-range cases passed')
