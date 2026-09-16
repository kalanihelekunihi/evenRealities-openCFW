# SPDX-License-Identifier: MIT
"""Execute the complete board wrapper, status decoder and analog update leaf."""
import json
import random
import re
import subprocess
from itertools import product
from build_gx8002_backup_board_initialize import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,values,seed):
    rng=random.Random(seed);r={f'r{i}':rng.getrandbits(32) for i in range(32)}
    initial=r.copy();pc=entry;saved=None;trace=[];calls=[]
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r15' and saved is None;saved=r['r15'];r['r14']=(r['r14']-4)&0xffffffff
        elif op=='pop':
            assert args=='r15' and saved is not None and not calls
            r['r15']=saved;r['r14']=(r['r14']+4)&0xffffffff
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return trace
        elif op=='bsr':calls.append(nxt);r['r15']=nxt;nxt=int(args,0)
        elif op=='rts':assert calls and r['r15']==calls[-1];nxt=calls.pop()
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('andi','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a&b if op=='andi' else a<<b)&0xffffffff
        elif op in ('br','bez','bnez'):
            if op=='br' or (r[p[0]]==0)==(op=='bez'):nxt=int(p[-1],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();address=(r[base]+int(off,0))&0xffffffff
            if op=='ld.w':r[reg]=values[address];trace.append(('read',address,r[reg]))
            else:trace.append(('write',address,r[reg]))
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('Board execution bound')


def verify():
    candidate=build();path=ROOT/'build/gx8002-backup-board-initialize/board.elf'
    assert sha(path.read_bytes())==candidate['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old={}
    for a,b in ((0x3be14,0x3be20),(0x3c8f8,0x3c93c),(0x3db18,0x3db2c)):
        old.update(decode(subprocess.check_output([tool,'-D',f'--start-address={a:#x}',f'--stop-address={b:#x}',str(wrapper)],text=True)))
    new=decode(subprocess.check_output([tool,'-d',str(path)],text=True));cases=0
    for flags,high,fallback,seed in product(range(16),(0,0xfffffff0),(0,1,0xffffffff),(0,1,0x12345678)):
        values={0xa0000034:flags|high,0xa001002c:fallback}
        wanted=[('read',0xa0000034,flags|high)]+([] if flags else [('read',0xa001002c,fallback)])
        wanted += [('write',0xa0005040+i*4,89) for i in range(4)]
        assert execute(old,0x3be14,values,seed)==execute(new,0x100034d4,values,seed)==wanted
        cases+=1
    return {'candidate':candidate,'cases':cases,'stock_sha256':IMAGE_SHA,'source_admitted':False,'limits':['All three compiled source routines execute in the same decoded register frame; no helper-return model. Checks exact ordered MMIO and preserved registers. No physical analog latch effects or asynchronous hardware qualification. Incoming references and integration pending.']}


if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-backup-board-initialize-execution.json').write_text(json.dumps(result,indent=2)+'\n');print(result['cases'],'complete board cluster cases')
