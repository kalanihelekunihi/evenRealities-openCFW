# SPDX-License-Identifier: MIT
"""Decoded completion callback preserves full port after byte-wide lookup."""
import json,subprocess
from itertools import product
from build_gx8002_uart_body_done import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,port,private,result):
    r={f'r{i}':0xabc00000+i for i in range(32)};r.update(r0=port,r1=private,r14=0x20070000);initial=r.copy();saved=None;pc=entry;events=[]
    for _ in range(25):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('Frame')
            saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            if args!='r4, r15' or saved is None:raise ValueError('Restore')
            r['r4'],r['r15']=saved;r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],events
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op in ('addi','subi'):r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(1 if op=='addi' else -1)*int(p[-1],0))&0xffffffff
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry<0x100000 else 0))&0xffffffff
            if target==0x10207ac0:events.append(('get',r['r0']));value={0:0x2002e050,1:0x2002e1cc}.get(r['r0'],0)
            elif target==0x10207b38:events.append(('body',r['r0'],r['r1'],r['r2']));value=result
            else:raise ValueError('Target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=value
        else:raise ValueError(('Opcode',op))
        pc=nxt
    raise ValueError('Bound')

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x111dc','--stop-address=0x11200',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-uart-body-done/buffers.disassembly.txt').read_text());cases=0
    for low,high,private,result in product(range(256),(0,0x100,0x80000000,0xffffff00),(0,0x20040000,0xffffffff),(0,1,0x80000000,0xffffffff)):
        port=high|low;events=[('get',low)]
        if low<2:events.append(('body',port,0x2002e050+380*low+60,0))
        expected=(0 if low<2 else 0xffffffff,events)
        for code,base in ((old,0),(new,0x101f6a74)):
            if execute(code,0x111dc+base,port,private,result)!=expected:raise ValueError('Callback')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['All byte ports and four high-bit patterns, ignored private pointer/body results, helper clobbers and saved ABI checked. Body/lookup modeled; high-bit port preservation does not qualify out-of-range body arrays or physical UART callbacks.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-body-done-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
