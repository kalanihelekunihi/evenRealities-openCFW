# SPDX-License-Identifier: MIT
"""Qualify relocated GRUS gate; module lookup remains modeled."""
import json,re,struct
from itertools import product
from link_gx8002_dma_uart_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from compare_gx8002_platform_gate import oracle

def execute(code,start,jumps,table,module,enable,source,delta,table_base,jump_base,lookup,shift_result=0):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=module,r1=enable,r14=0x8000)
    initial=r.copy();memory={};trace=[];saved=None;pc=start;condition=False;return_pc=None
    def byte(a):
        if table_base<=a<table_base+len(table):return table[a-table_base]
        if jump_base<=a<jump_base+len(jumps):return jumps[a-jump_base]
        if a in memory:return memory[a]
        raise ValueError('unmapped read')
    def word(a):return sum(byte(a+i)<<(8*i) for i in range(4))
    def store(a,v):
        for i in range(4):memory[a+i]=(v>>(8*i))&255
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r4-r6, r15':raise ValueError('unexpected save')
            saved={k:r[k] for k in ('r4','r5','r6','r15')}
        elif op=='pop':
            if args!='r4-r6, r15' or saved is None:raise ValueError('unexpected restore')
            r.update(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15)):raise ValueError('ABI mismatch')
            return trace
        elif op=='rts':
            if return_pc is None or r['r15']!=return_pc:raise ValueError('Unexpected lookup return')
            following=return_pc;return_pc=None
        elif op=='movih':r[p[0]]=int(p[1],0)<<16
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='sextb':r[p[0]]=(r[p[1]]&255)-(256 if r[p[1]]&128 else 0)&0xffffffff
        elif op in ('addu','lsli','addi','subi','andi','andni','ori','lsl','lsr','bseti','bclri'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            if op in ('lsl','lsr') and b>=32:
                r[p[0]]=shift_result;pc=following;continue
            r[p[0]]=(a+b if op in ('addi','addu') else a-b if op=='subi' else a&b if op=='andi' else a&~b if op=='andni' else a|b if op=='ori' else a<<b if op in ('lsl','lsli') else a>>b if op=='lsr' else a|(1<<b) if op=='bseti' else a&~(1<<b))&0xffffffff
        elif op in ('inct','incf'):
            if condition == (op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&0xffffffff
        elif op in ('cmphs','cmphsi','cmpne','cmpnei'):
            a=r[p[0]];b=r[p[1]] if p[1].startswith('r') else int(p[1],0);condition=a>=b if op in ('cmphs','cmphsi') else a!=b
        elif op in ('bt','bf','br','bez','bnez'):
            take={'bt':condition,'bf':not condition,'br':True}.get(op)
            if take is None:take=r[p[0]]==0 if op=='bez' else r[p[0]]!=0
            if take:following=int(p[-1],0)
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&0xffffffff
            if r[p[0]]:following=int(p[1],0)
        elif op=='jmp':
            following=r[p[0]]-delta
            if following not in code:raise ValueError('invalid switch target')
        elif op in ('ld.w','ldr.w','ld.b','ld.bs','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+|r\d+ << [02])\)',args)
            if not m:raise ValueError('unsupported memory operand')
            reg,base,off=m.groups();a=r[base]+(r[off.split()[0]]<<int(off.split()[-1]) if '<<' in off else int(off,0))
            if op=='st.w':
                if 0x7fe8<=a<0x8000:
                    store(a,r[reg]);pc=following;continue
                if a not in (0xa001001c,0xa0010020,0xa030001c,0xa0300020):raise ValueError('unexpected write')
                trace.append(('write',a,r[reg]))
            elif a in (0xa001008c,0xa0300088):r[reg]=source;trace.append(('read',a,source))
            elif op in ('ld.b','ld.bs'):
                value=byte(a);r[reg]=(value-256 if op=='ld.bs' and value&128 else value)&0xffffffff
            else:r[reg]=word(a)
        elif op=='bsr':
            if int(p[0],0)!=lookup or r['r1']!=r['r14']:raise ValueError('unexpected lookup call')
            trace.append(('lookup',r['r0']))
            if return_pc is not None:raise ValueError('Nested lookup')
            return_pc=following;r['r15']=following;following=lookup
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def verify():
    link=build();path=ROOT/'build/gx8002-dma-uart-source/dma-uart.elf'
    elf=Elf32(path.read_bytes(),str(path));symbols={s['name']:s for s in elf.symbols() if s['name']}
    data=next(s for s in elf.sections if s['name']=='.data');ro=next(s for s in elf.sections if s['name']=='.rodata')
    table_base=symbols['gx_clock_param_table']['value'];start=table_base-data['address']
    table=elf.contents(data)[start:start+416];jumps=elf.contents(ro)
    code=decode((ROOT/'build/gx8002-dma-uart-source/dma-uart.disassembly.txt').read_text())
    gate=symbols['open_cfw_gx8002_platform_gate']['value'];lookup=symbols['__module_get_info']['value'];cases=0
    for module,enable,source,shift_result in product((*range(28),0x7fffffff,0x80000000,0xffffffff),(0,1,2,0xffffffff),(0,0xffffffff,0x55555555,0xaaaaaaaa,*[1<<i for i in range(32)],*[(~(1<<i))&0xffffffff for i in range(32)]),(0,0xffffffff)):
        result=execute(code,gate,jumps,table,module,enable,source,0,table_base,ro['address'],lookup,shift_result)
        if result!=oracle(table,module,enable,source):raise ValueError(('Relocated clock mismatch',module,enable,source,result))
        cases+=1
    return {'link':link,'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Module lookup and gate execute in one register/memory frame against the linked source table. Finite source-register patterns; no concurrency or physical clock proof. Out-of-range shift intermediates tested as both zero and UINT32_MAX; their architecture semantics are not claimed. Modules 1 and 5 discard these intermediates without MMIO use.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-uart-clock-link.json').write_text(json.dumps(result,indent=2)+'\n');print('Relocated clock cases:',result['cases'])
