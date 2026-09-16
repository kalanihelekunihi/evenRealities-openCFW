#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare gate instruction traces; qualified module lookup is modeled."""
import json
import re
import struct
import subprocess
from build_gx8002_backup_platform_gate import build,IMAGE_SHA,sha
from link_gx8002_uart_console import ROOT
from analyze_gx8002_upstream_objects import IMAGE
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,start,jumps,table,module,enable,source,delta,lookup_hook=None,record_base=0x2001699c,jump_base=0x1001295c,lookup_entry=0x100034e0):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=module,r1=enable,r14=0x8000)
    initial=r.copy();memory={};trace=[];saved=None;pc=start;condition=False
    def byte(a):
        if record_base<=a<record_base+416:return table[a-record_base]
        if jump_base<=a<jump_base+148:return jumps[a-jump_base]
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
            if int(p[0],0)!=lookup_entry-delta or r['r1']!=r['r14']:raise ValueError('unexpected lookup call')
            mod=r['r0'];out=r['r1'];trace.append(('lookup',mod));result=0xffffffff
            if lookup_hook is not None:
                result,values,writes=lookup_hook(mod)
                for address,value in writes:
                    assert 0x1000<=address<0x1018
                    store(out+address-0x1000,value)
            elif mod<26:
                ids=[struct.unpack_from('<I',table,i*16)[0] for i in range(26)]
                index=mod if ids[mod]==mod else next((i for i,v in enumerate(ids) if v==mod),None)
                store(out,0)
                if index is not None:
                    base=0xa0010000 if mod<10 else 0xa0300000
                    for i,v in enumerate((record_base+16*index,base,base+(0x8c if mod<10 else 0x88),base+24,base+28,base+32)):store(out+i*4,v)
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


def verify(lookup_hook=None):
    candidate=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-platform-gate';p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    e=Elf32(p.read_bytes(),str(p));assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3c528','--stop-address=0x3c630',str(p)],text=True))
    new=decode((out/'gate.disassembly.txt').read_text())
    e=Elf32((out/'gate.elf').read_bytes(),'gate');jumps=e.contents(next(s for s in e.sections if s['name']=='.rodata'))
    table_offset=0x2001699c-0x20003000+0x3b940
    table=stock[table_offset:table_offset+416]
    jump_offset=0x1001295c-0x10003000+0x3b940
    cases=0
    for module in [*range(28),0x7fffffff,0x80000000,0xffffffff]:
      for enable in (0,1,2,0xffffffff):
       for source in [0,0xffffffff,0x55555555,0xaaaaaaaa,*[1<<i for i in range(32)],*[(~(1<<i))&0xffffffff for i in range(32)]]:
        expected=oracle(table,module,enable,source)
        a=execute(old,0x3c528,stock[jump_offset:jump_offset+148],table,module,enable,source,0x10003000-0x3b940,lookup_hook=lookup_hook)
        b=execute(new,0x10003be8,jumps,table,module,enable,source,0,lookup_hook=lookup_hook)
        assert a==b==expected,(module,enable,source,a,b,expected)
        cases+=1
    report={'candidate':candidate,'cases':cases,'stock_table_offset':table_offset,'stock_table_sha256':sha(table),
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Backup module lookup modeled using authenticated stock table, not yet qualified source.',
                      'Ordered MMIO and lookup traces with source-generated branch tables; physical clocks, table mutations and placement remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-platform-gate-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(verify()['cases'],'backup gate cases passed')
