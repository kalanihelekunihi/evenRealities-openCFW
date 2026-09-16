#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute decoded clock lookup bodies against independent output oracles."""
import json
import re
import struct
import subprocess
from build_gx8002_backup_clock_tables import build as tables,Elf32,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE
from link_gx8002_uart_console import ROOT


def execute(code,start,module,pointer,ids,record_base=0x2001699c):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=module,r1=pointer)
    initial=r.copy();memory={record_base+i*16:v for i,v in enumerate(ids)}
    memory.update({0x1000+i*4:0xa5a5a5a5 for i in range(6)})
    writes=[];pc=start;condition=False
    for _ in range(400):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','addu','lsli','bseti'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addi','addu') else a-b if op=='subi' else a<<b if op=='lsli' else a|(1<<b))&0xffffffff
        elif op in ('cmphsi','cmphs','cmpne'):
            a=r[p[0]];b=r[p[1]] if p[1].startswith('r') else int(p[1],0)
            condition=a!=b if op=='cmpne' else a>=b
        elif op in ('br','bt','bf','bez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&0xffffffff
            take={'br':True,'bt':condition,'bf':not condition}.get(op)
            if take is None:take=r[p[0]]==0 if op=='bez' else r[p[0]]!=0
            if take:following=int(p[-1],0)
        elif op in ('ld.w','ldr.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+|r\d+ << 0)\)',args)
            if not m:raise ValueError('unsupported memory operand')
            reg,base,off=m.groups();address=(r[base]+(r[off.split()[0]] if '<<' in off else int(off,0)))&0xffffffff
            if address not in memory:raise ValueError('unmapped access')
            if op=='st.w':
                if not 0x1000<=address<0x1018:raise ValueError('unexpected write')
                memory[address]=r[reg];writes.append((address,r[reg]))
            else:r[reg]=memory[address]
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),15)):raise ValueError('ABI mismatch')
            return r['r0'],[memory[0x1000+i*4] for i in range(6)],writes
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def verify():
    evidence=tables();output=ROOT/'build/gx8002-backup-clock-tables';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    elf=Elf32(wrapper.read_bytes(),str(wrapper));assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x3be20','--stop-address=0x3bee0',str(wrapper)],text=True))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d','--section=.text',str(output/'tables.elf')],text=True))
    offset=0x2001699c-0x20003000+0x3b940
    original=[struct.unpack_from('<I',stock,offset+i*16)[0] for i in range(26)];cases=0
    variants=[original,list(range(26)),list(reversed(range(26))),[0xffffffff]*26]
    variants += [[m if i in (j,25) else 0xffffffff for i in range(26)] for m in range(26) for j in range(26)]
    for ids in variants:
        for module in [*range(28),0x7fffffff,0x80000000,0xffffffff]:
            for pointer in (0,0x1000):
                expected=[0xa5a5a5a5]*6;writes=[];result=0xffffffff
                if pointer and module<26:
                    expected[0]=0;writes=[(pointer,0)]
                    index=module if ids[module]==module else next((i for i,v in enumerate(ids) if v==module),None)
                    if index is not None:
                        base=0xa0010000 if module<10 else 0xa0300000
                        expected=[0x2001699c+index*16,base,base+(0x8c if module<10 else 0x88),base+24,base+28,base+32]
                        writes += [(pointer+i*4,v) for i,v in enumerate(expected)];result=0
                oracle=(result,expected,writes)
                if execute(old,0x3be20,module,pointer,ids)!=oracle or execute(new,0x100034e0,module,pointer,ids)!=oracle:raise ValueError('clock lookup mismatch')
                cases+=1
    report={'evidence':evidence,'cases':cases,'source_admitted':False,'limits':['Finite decoded execution; ordinary RAM reads may be optimized.', 'No concurrent table mutation, overlapping output, hardware or timing qualification.']}
    (ROOT/'docs/research/gx8002-backup-clock-lookup-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
