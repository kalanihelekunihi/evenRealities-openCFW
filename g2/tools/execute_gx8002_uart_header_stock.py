# SPDX-License-Identifier: MIT
"""Decoded stock inlined header path, stopping before caller state transitions."""
import re, subprocess
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import ROOT, IMAGE_SHA, sha
from build_transparent_image import Elf32


def execute(port, count, payload, crc_result):
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    section=next(sec for sec in elf.sections if sec['name']=='.data')
    if sha(elf.contents(section))!=IMAGE_SHA:raise ValueError('Stock header wrapper identity changed')
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x116d6','--stop-address=0x11764',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    r={f'r{i}':0x90000000+i for i in range(32)}
    r.update(r0=port,r1=0x20040000,r2=0x20041000,r3=0x20041004,r14=0x2002f000)
    r.update(r4=0x2003ffe4,r5=0x20040a78,r6=0x20040000,r7=port,r10=0x20026c74,r14=0x20041004)
    initial=r.copy()
    memory={}; calls=[]
    def put(addr,value,size):
        for i in range(size):memory[addr+i]=(value>>(8*i))&255
    def get(addr,size):return sum(memory[addr+i]<<(8*i) for i in range(size))
    for i in range(14):put(0x20040000+i,0xa5,1)
    for i,b in enumerate(payload):put(0x20042000+i,b,1)
    put(0x20041000,0x20042000,4);put(0x20041004,len(payload),4)
    put(0x20026c74+port*4,count,4)
    saved=None;condition=False;pc=0x116d6
    for _ in range(1000):
        if pc in (0x116a4,0x11802,0x1173c):
            result={0x116a4:0,0x11802:1,0x1173c:0xffffffff}[pc]
            return {'result':result,'header':bytes(get(0x20040000+i,1) for i in range(14)),
                    'count':get(0x20026c74+port*4,4),'remaining':get(0x20041004,4),
                    'consumed_pointer':get(0x20041000,4)-0x20042000,'crc_calls':calls}
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4-r5, r15':raise ValueError('Probe frame')
            saved=[r[x] for x in ('r4','r5','r15')];r['r14']-=12
        elif op=='pop':
            if args!='r4-r5, r15' or saved is None:raise ValueError('Probe restore')
            for reg,value in zip(('r4','r5','r15'),saved):r[reg]=value
            r['r14']+=12
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):
                raise ValueError('Probe callee-preserved register changed')
            return {'result':r['r0'],'header':bytes(get(0x20040000+i,1) for i in range(14)),
                    'count':get(0x20026c74+port*4,4),'remaining':get(0x20041004,4),
                    'consumed_pointer':get(0x20041000,4)-0x20042000,'crc_calls':calls}
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','subu','addi','subi','lsli','or'):
            left=r[p[-2]] if len(p)==3 else r[p[0]]
            right=r[p[-1]] if p[-1] in r else int(p[-1],0)
            value={'addu':lambda:left+right,'addi':lambda:left+right,'subu':lambda:left-right,
                   'subi':lambda:left-right,'lsli':lambda:left<<right,'or':lambda:left|right}[op]()
            r[p[0]]=value&0xffffffff
        elif op in ('cmpnei','cmpne','cmphsi','cmphs'):
            right=r[p[1]] if p[1] in r else int(p[1],0)
            condition=(r[p[0]]!=right) if op in ('cmpnei','cmpne') else r[p[0]]>=right
        elif op in ('bt','bf','br'):jump=int(p[0],0) if op=='br' or condition==(op=='bt') else None
        elif op in ('bez','bnez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&0xffffffff
            if (r[p[0]]==0)==(op=='bez'):jump=int(p[1],0)
        elif op=='bsr':
            if int(args,0)!=0x12e34:raise ValueError('Probe CRC target')
            if (r['r0'],r['r1'],r['r2'])!=(0,0x20040000,10):raise ValueError('Probe CRC arguments')
            calls.append((r['r0'],r['r2']))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=crc_result
        elif op.startswith(('ld','st')):
            match=re.fullmatch(r'(r\d+), \((r\d+)(?:, (r\d+) << (\d+)|, (0x[0-9a-f]+))?\)',args)
            if not match:raise ValueError('Probe memory operand '+args)
            reg,base,index,shift,offset=match.groups()
            address=r[base]+((r[index]<<int(shift)) if index else int(offset or '0',0))
            size=1 if op.endswith('.b') else 4
            if op.startswith('ld'):r[reg]=get(address,size)
            else:put(address,r[reg],size)
            if 'bi.' in op:r[base]+=size
        else:raise ValueError('Probe instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Probe instruction bound')
