# SPDX-License-Identifier: MIT
"""Backup frequency instruction execution with separately executed lookup helper.

Derived from the primary frequency interpreter; backup frames and inline
divider are executed directly. No primary verifier is modified.
"""
import json
import struct
from itertools import product
from link_gx8002_uart_console import ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
SP=0x2002f7fc


def execute(code,table,module,lookup_result,offset_byte,source_word=0,divider=0,selection_word=0,dto_present=False,dto_word=0,pll_words=None,selection_values=None,read_trace=None,divider_hook=None,divider_descriptor=None,lookup_ids=None,lookup_records=None,source_cells=None,mmio_trace=None,entry=0x10003cf0,lookup_entry=0x100034e0,divider_entry=0x10024ae8,record_base=0x2001699c,jump_base=0x100129f0, delta=0, lookup_hook=None, mmio_sequences=None):
    r={f'r{i}':(0x81234567+i*0x1020304)&MASK for i in range(32)};r.update(r0=module,r14=SP)
    initial=r.copy();memory={0xa001008c:source_word,0xa0300088:selection_word,0x2003100c:0x20031100 if dto_present else 0,0x20031100:0x24,0xa0300024:dto_word};pc=entry;condition=False;calls=[]
    if pll_words is not None:
        memory.update(dict(zip((0xa000501c,0xa0005020,0xa0005024,0xa0005028,0xa0005030),pll_words)))
        memory.update({0x10025e38+i*4:v for i,v in enumerate((61440000,73728000,86016000,98304000))})
    if divider_descriptor is not None:
        present,off,shift,mask,word=divider_descriptor
        memory.update({0x20031008:0x20031200 if present else 0,0x20031200:off,0x20031201:shift,0x20031202:mask,0xa0300000+off:word})
    if lookup_records is not None:
        lookup_ids=[struct.unpack_from('<I',lookup_records,i*16)[0] for i in range(26)]
        memory.update({record_base+i*16+6:lookup_records[i*16+6] for i in range(26)})
    if source_cells is not None:
        memory.update({address:value for (address,width),value in source_cells.items()})
    active_helper=None
    if lookup_ids is not None:
        memory.update({record_base+16*i:v for i,v in enumerate(lookup_ids)})
    selection_iterator=iter(selection_values) if selection_values is not None else None
    read_indices={}
    def load(address,width=4):
        expected_width=1 if lookup_records is not None and record_base<=address<record_base+416 and (address-record_base)%16==6 else 1 if address in (0x20031100,0x20031200,0x20031201) else 2 if address==0x20031202 else 4
        if source_cells is not None and any(a==address for a,w in source_cells):
            if (address,width) not in source_cells:raise ValueError('Source table read width')
            expected_width=width
            memory[address]=source_cells[address,width]
        if width!=expected_width:raise ValueError('Continuous frame read width')
        if address==0xa0300088 and selection_iterator is not None:
            memory[address]=next(selection_iterator)
        if mmio_sequences is not None and address in mmio_sequences:
            assert address>=0xa0000000 and width==4
            index=read_indices.get(address,0);sequence=mmio_sequences[address]
            if index>=len(sequence):raise ValueError('MMIO sequence exhausted')
            memory[address]=sequence[index];read_indices[address]=index+1
        if read_trace is not None and address in (0xa001008c,0xa0300088):read_trace.append((address,memory[address]))
        if address not in memory:raise ValueError(('Early-frame unmapped read',hex(address),width))
        if mmio_trace is not None and address>=0xa0000000:mmio_trace.append((address,width,memory[address]))
        return memory[address]
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('push','pop'):
            import re
            registers=[]
            for group in args.split(', '):
                match=re.fullmatch(r'r(\d+)(?:-r(\d+))?',group)
                if not match:raise ValueError('Unexpected frame operand')
                registers += ['r'+str(i) for i in range(int(match[1]),int(match[2] or match[1])+1)]
            if op=='push':
                r['r14']-=4*len(registers)
                for i,reg in enumerate(registers):memory[r['r14']+4*i]=r[reg]
            else:
                for i,reg in enumerate(registers):r[reg]=load(r['r14']+4*i)
                r['r14']+=4*len(registers)
                if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Backup frequency ABI')
                return r['r0'],calls
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b)&MASK
        elif op in ('andi','andni','lsli','lsri','rotli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a&b if op=='andi' else a&~b if op=='andni' else a<<b if op=='lsli' else a>>b if op=='lsri' else (a<<b)|(a>>(32-b)))&MASK
        elif op in ('lsr','lsl','and','divu','addu','or','mult','nor'):
            a,b=(r[p[1]],r[p[2]]) if len(p)==3 else (r[p[0]],r[p[1]])
            r[p[0]]=(a>>b if op=='lsr' else a<<b if op=='lsl' else a&b if op=='and' else a+b if op=='addu' else a|b if op=='or' else a*b if op=='mult' else ~(a|b) if op=='nor' else a//b)&MASK
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op=='mul.u32':
            value=r[p[1]]*r[p[2]];r[p[0]]=value&MASK;r['r'+str(int(p[0][1:])+1)]=value>>32
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('inct','incf'):
            if condition if op=='inct' else not condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','bf','br'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op in ('bnez','bez'):
            if (r[p[0]]!=0 if op=='bnez' else r[p[0]]==0):nxt=int(p[1],0)
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&MASK
            if r[p[0]]:nxt=int(p[1],0)
        elif op=='ldr.w':
            if args=='r3, (r2, r3 << 2)' and r['r2']==jump_base and r['r3']<19:r['r3']=table[r['r3']]
            elif args=='r2, (r12, r2 << 2)' and r['r12']==0x10025e38 and r['r2']<4:r['r2']=load(r['r12']+4*r['r2'])
            elif lookup_ids is not None and '<< 0)' in args:
                import re
                m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 0\)',args)
                if not m:raise ValueError('Lookup indexed operand')
                r[m[1]]=load((r[m[2]]+r[m[3]])&MASK)
            else:raise ValueError('Continuous frame indexed read')
        elif op=='jmp':nxt=r[args]-delta
        elif op=='bsr':
            target=int(args,0)
            if target!=lookup_entry-delta or lookup_hook is None:raise ValueError('Backup lookup binding')
            if r['r1']!=r['r14']:raise ValueError('Backup lookup frame')
            calls.append(('lookup',r['r0']))
            result,values,writes=lookup_hook(r['r0'])
            for address,value in writes:
                assert 0x1000<=address<0x1018
                memory[r['r1']+address-0x1000]=value
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        elif op=='rts':
            if active_helper is None:raise ValueError('Unexpected leaf return')
            if active_helper=='divider':calls.append(('divider',r['r0']))
            active_helper=None;nxt=r['r15']
        elif op=='st.w':
            import re
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Lookup store operand')
            address=(r[m[2]]+int(m[3],0))&MASK
            if active_helper!='lookup' or not SP-36<=address<SP-12 or address%4:raise ValueError('Lookup store outside info')
            memory[address]=r[m[1]]
        elif op in ('ld.w','ld.b','ld.h'):
            import re
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Low-frame load operand')
            reg,base,off=m.groups();address=r[base]+int(off,0)
            r[reg]=load(address,1 if op=='ld.b' else 2 if op=='ld.h' else 4)
        elif op=='ld.bs':
            import re
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Signed byte operand')
            byte=load(r[m[2]]+int(m[3],0),1)
            r[m[1]]=(byte if byte<128 else byte-256)&MASK
        else:raise ValueError('Early-frame path left qualified instructions: '+op)
        pc=nxt
    raise ValueError('Early-frame execution bound')
