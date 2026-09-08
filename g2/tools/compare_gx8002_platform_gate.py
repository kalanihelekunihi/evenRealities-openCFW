#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare gate instruction traces; qualified module lookup is modeled."""
import json
import re
import struct
import subprocess
from link_gx8002_platform_gate import link
from link_gx8002_uart_console import ROOT
from analyze_gx8002_upstream_objects import IMAGE
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,start,jumps,table,module,enable,source,delta):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=module,r1=enable,r14=0x8000)
    initial=r.copy();memory={};trace=[];saved=None;pc=start;condition=False
    def byte(a):
        if 0x200266e0<=a<0x20026880:return table[a-0x200266e0]
        if 0x100253cc<=a<0x10025460:return jumps[a-0x100253cc]
        if a in memory:return memory[a]
        raise ValueError('unmapped read')
    def word(a):return sum(byte(a+i)<<(8*i) for i in range(4))
    def store(a,v):
        for i in range(4):memory[a+i]=(v>>(8*i))&255
    for _ in range(200):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r4-r6, r15':raise ValueError('unexpected save')
            saved={k:r[k] for k in ('r4','r5','r6','r15')}
        elif op=='pop':
            if args!='r4-r6, r15' or saved is None:raise ValueError('unexpected restore')
            r.update(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15)):raise ValueError('ABI mismatch')
            return trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='sextb':r[p[0]]=(r[p[1]]&255)-(256 if r[p[1]]&128 else 0)&0xffffffff
        elif op in ('addi','subi','andi','andni','ori','lsl','lsr','bseti','bclri'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            if op in ('lsl','lsr') and b>=32:raise ValueError('unqualified shift')
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a&b if op=='andi' else a&~b if op=='andni' else a|b if op=='ori' else a<<b if op=='lsl' else a>>b if op=='lsr' else a|(1<<b) if op=='bseti' else a&~(1<<b))&0xffffffff
        elif op in ('cmphsi','cmpne','cmpnei'):
            a=r[p[0]];b=r[p[1]] if p[1].startswith('r') else int(p[1],0);condition=a>=b if op=='cmphsi' else a!=b
        elif op in ('bt','bf','br','bez','bnez'):
            take={'bt':condition,'bf':not condition,'br':True}.get(op)
            if take is None:take=r[p[0]]==0 if op=='bez' else r[p[0]]!=0
            if take:following=int(p[-1],0)
        elif op=='jmp':
            following=r[p[0]]-delta
            if following not in code:raise ValueError('invalid switch target')
        elif op in ('ld.w','ldr.w','ld.b','ld.bs','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+|r\d+ << 2)\)',args)
            if not m:raise ValueError('unsupported memory operand')
            reg,base,off=m.groups();a=r[base]+(r[off.split()[0]]<<2 if '<<' in off else int(off,0))
            if op=='st.w':
                if a not in (0xa001001c,0xa0010020,0xa030001c,0xa0300020):raise ValueError('unexpected write')
                trace.append(('write',a,r[reg]))
            elif a in (0xa001008c,0xa0300088):r[reg]=source;trace.append(('read',a,source))
            elif op in ('ld.b','ld.bs'):
                value=byte(a);r[reg]=(value-256 if op=='ld.bs' and value&128 else value)&0xffffffff
            else:r[reg]=word(a)
        elif op=='bsr':
            if int(p[0],0)!=0x10024a44-delta or r['r1']!=r['r14']:raise ValueError('unexpected lookup call')
            mod=r['r0'];out=r['r1'];trace.append(('lookup',mod));result=0xffffffff
            if mod<26:
                ids=[struct.unpack_from('<I',table,i*16)[0] for i in range(26)]
                index=mod if ids[mod]==mod else next((i for i,v in enumerate(ids) if v==mod),None)
                store(out,0)
                if index is not None:
                    base=0xa0010000 if mod<10 else 0xa0300000
                    for i,v in enumerate((0x200266e0+16*index,base,base+(0x8c if mod<10 else 0x88),base+24,base+28,base+32)):store(out+i*4,v)
                    result=0
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def oracle(table,module,enable,source):
    parent={7:2,8:2,17:16,18:16,20:19,21:19,23:22,24:22}.get(module,module)
    ids=[struct.unpack_from('<I',table,i*16)[0] for i in range(26)]
    result=[('lookup',parent)]
    if parent<26:
        i=ids.index(parent);high,allbit,clk=struct.unpack_from('<bbb',table,i*16+4)
        if clk!=-1:
            base=0xa0010000 if parent<10 else 0xa0300000
            result.append(('read',base+(0x8c if parent<10 else 0x88),source))
            selected=2 if parent in (0,1,6,9) and source&(1<<(clk+1)) else (source>>clk)&1
            result.append(('write',base+(32 if selected==1 and enable else 28),1<<high))
    result.append(('lookup',module))
    if module<26 and module not in (1,5):
        i=ids.index(module);bit=table[i*16+5];mask=1<<bit
        extra={6:15,17:16,18:17,11:3,20:18,21:19,13:13,14:15,23:20,24:21}.get(module)
        if extra is not None:mask|=1<<extra
        result.append(('write',(0xa0010000 if module<10 else 0xa0300000)+(32 if enable else 28),mask))
    return result


def verify():
    placement=link();output=ROOT/'build/gx8002-platform-gate';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    stock=IMAGE.read_bytes();table=stock[0x186f4:0x18894]
    wrapper=output/'stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    wrapped=bytearray(wrapper.read_bytes());struct.pack_into('<I',wrapped,36,0x21006009);wrapper.write_bytes(wrapped)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x17094','--stop-address=0x17194',str(output/'stock.elf')],text=True))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d',str(output/'gate-fit.elf')],text=True))
    elf=Elf32((output/'gate-fit.elf').read_bytes(),'gate-fit');jumps=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_platform_gate'))
    cases=0
    for module in [*range(28),0x7fffffff,0x80000000,0xffffffff]:
        for enable in (0,1,2,0xffffffff):
            for source in [0,0xffffffff,0x55555555,0xaaaaaaaa,*[1<<i for i in range(32)],*[(~(1<<i))&0xffffffff for i in range(32)]]:
                expected=oracle(table,module,enable,source)
                if execute(old,0x17094,stock[0x173e0:0x17474],table,module,enable,source,0x1000dfec)!=expected or execute(new,0x10025080,jumps,table,module,enable,source,0)!=expected:raise ValueError('gate trace mismatch')
                cases+=1
    report={'placement':placement,'cases':cases,'source_admitted':False,'limits':['Qualified lookup modeled with original table; finite source-register patterns.','No concurrent table mutation, timing, or hardware qualification.']}
    (ROOT/'docs/research/gx8002-platform-gate-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
