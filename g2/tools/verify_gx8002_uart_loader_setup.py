# SPDX-License-Identifier: MIT
"""Decode primary loader setup, branch, argument lifetime and entry dispatch."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,stock,mode,seed):
    r={f'r{i}':(seed+i*0x10203)&0xffffffff for i in range(32)};r['r14']=0x20010000;initial=r.copy();pc=0x9fd0;calls=[];saved=None;condition=False;memory={0x20001284:0,0x20033ffc:mode}
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':assert args=='r4-r6, r15';saved={k:r[k] for k in ('r4','r5','r6','r15')};r['r14']-=16
        elif op=='pop':
            assert r['r14']==initial['r14']-16;r.update(saved);r['r14']+=16
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],calls,memory
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','addu','subu','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0);r[p[0]]=(a-b if op in ('subi','subu') else a<<b if op=='lsli' else a+b)&0xffffffff
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','br'):
            if op=='br' or condition:nxt=int(p[-1],0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0)
            if op=='ld.w':r[reg]=memory[address]
            else:assert address==0x2002e938;memory[address]=r[reg]
        elif op=='bsr':
            assert int(args,0)==0xa1e4;offset,dest,length=r['r0'],r['r1'],r['r2'];calls.append(('read',offset,dest,length))
            data=stock[0x958c+offset:0x958c+offset+length];assert len(data)==length and length%4==0
            for i in range(0,length,4):memory[dest+i]=int.from_bytes(data[i:i+4],'little')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xbad00000+i
        elif op=='jsr':
            assert r[p[0]]==0x10023500;calls.append(('entry',r[p[0]]))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xbad10000+i
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('loader bound')

def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-D','--start-address=0x9fd0','--stop-address=0xa04c',str(path)],text=True));cases=0
    for mode in (0,1,0xffffffff,0xaabbccdc):
        for seed in (0,91,0xffffffff):
            result,calls,memory=execute(code,stock,mode,seed)
            assert result==0 and calls==[('read',0x3000,0x2000ffec,4),('read',0xbe88,0x10023400,0x397c),('entry',0x10023500)]
            assert memory[0x2002e938]==0x10023500
            actual=b''.join(memory[a].to_bytes(4,'little') for a in range(0x10026a94,0x10026b94,4));assert actual==stock[0x18aa8:0x18ba8]
            cases+=1
    return {'stock_sha256':IMAGE_SHA,'routine_sha256':sha(stock[0x9fd0:0xa070]),'cases':cases,'source_admitted':False,'limits':['Stock primary setup/branch and argument lifetime executed with clobbering modeled flash reads and modeled returning entry. UART bytes transferred into modeled IRAM. Actual flash reader, secondary path and physical IRAM/DRAM alias remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-loader-setup.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
