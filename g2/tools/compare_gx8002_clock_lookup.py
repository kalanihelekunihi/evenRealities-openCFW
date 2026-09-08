#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute decoded clock lookup bodies against independent output oracles."""
import json
import re
import struct
import subprocess
from verify_gx8002_clock_tables import verify as tables
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE
from link_gx8002_uart_console import ROOT


def execute(code,start,module,pointer,ids):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=module,r1=pointer)
    initial=r.copy();memory={0x200266e0+i*16:v for i,v in enumerate(ids)}
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
    evidence=tables();output=ROOT/'build/gx8002-platform-gate';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper=output/'stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x16a58','--stop-address=0x16afc',str(wrapper)],text=True))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d','--section=.text.__module_get_info',str(output/'tables.elf')],text=True))
    stock=IMAGE.read_bytes();original=[struct.unpack_from('<I',stock,0x186f4+i*16)[0] for i in range(26)];cases=0
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
                        expected=[0x200266e0+index*16,base,base+(0x8c if module<10 else 0x88),base+24,base+28,base+32]
                        writes += [(pointer+i*4,v) for i,v in enumerate(expected)];result=0
                oracle=(result,expected,writes)
                if execute(old,0x16a58,module,pointer,ids)!=oracle or execute(new,0x10024a44,module,pointer,ids)!=oracle:raise ValueError('clock lookup mismatch')
                cases+=1
    report={'evidence':evidence,'cases':cases,'source_admitted':False,'limits':['Finite decoded execution; ordinary RAM reads may be optimized.', 'No concurrent table mutation, overlapping output, hardware or timing qualification.']}
    (ROOT/'docs/research/gx8002-clock-lookup-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
