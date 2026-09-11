# SPDX-License-Identifier: MIT
"""Continuous entry-to-return clock checks for low-frequency MMIO paths."""
import json
import struct
from itertools import product
from analyze_gx8002_clock_table_placement import analyze,ROOT,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
SP=0x2002f7fc


def execute(code,table,module,lookup_result,offset_byte,source_word=0,divider=0,selection_word=0,dto_present=False,dto_word=0,pll_words=None,selection_values=None,read_trace=None,divider_hook=None,divider_descriptor=None,lookup_ids=None,lookup_records=None,source_cells=None,mmio_trace=None,entry=0x10025210,lookup_entry=0x10024a44,divider_entry=0x10024ae8,record_base=0x200266e0,jump_base=0x10025460):
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
    def load(address,width=4):
        expected_width=1 if lookup_records is not None and record_base<=address<record_base+416 and (address-record_base)%16==6 else 1 if address in (0x20031100,0x20031200,0x20031201) else 2 if address==0x20031202 else 4
        if source_cells is not None and any(a==address for a,w in source_cells):
            if (address,width) not in source_cells:raise ValueError('Source table read width')
            expected_width=width
            memory[address]=source_cells[address,width]
        if width!=expected_width:raise ValueError('Continuous frame read width')
        if address==0xa0300088 and selection_iterator is not None:
            memory[address]=next(selection_iterator)
        if read_trace is not None and address in (0xa001008c,0xa0300088):read_trace.append((address,memory[address]))
        if address not in memory:raise ValueError(('Early-frame unmapped read',hex(address),width))
        if mmio_trace is not None and address>=0xa0000000:mmio_trace.append((address,width,memory[address]))
        return memory[address]
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4-r5, r15':raise ValueError('Early-frame push')
            r['r14']-=12
            for i,reg in enumerate(('r4','r5','r15')):memory[r['r14']+4*i]=r[reg]
        elif op=='pop':
            if args!='r4-r5, r15':raise ValueError('Early-frame pop')
            for i,reg in enumerate(('r4','r5','r15')):r[reg]=load(r['r14']+4*i)
            r['r14']+=12
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Early-frame ABI')
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
        elif op=='jmp':nxt=r[args]
        elif op=='bsr':
            target=int(args,0)
            if target==lookup_entry:
                if r['r1']!=SP-36:raise ValueError('Low-frame lookup ABI')
                calls.append(('lookup',r['r0']))
                if lookup_ids is not None:
                    active_helper='lookup';r['r15']=nxt;pc=target;continue
                for i,v in enumerate((0x20031000,0xa0300000,0xa0300088,0,0,0)):memory[r['r1']+4*i]=v
                result=lookup_result
            elif target==divider_entry:
                expected_args=(memory[SP-36],memory[SP-32]) if lookup_records is not None else (0x20031000,0xa0300000)
                if (r['r0'],r['r1'])!=expected_args:raise ValueError('Low-frame divider ABI')
                if divider_descriptor is not None or source_cells is not None:
                    active_helper='divider';r['r15']=nxt;pc=target;continue
                result=divider if divider_hook is None else divider_hook(r['r0'],r['r1'])
                calls.append(('divider',result))
            else:raise ValueError('Low-frame helper target')
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
            if args not in ('r2, (r0, 0x6)','r1, (r0, 0x6)'):raise ValueError('Clock parameter operand')
            if lookup_records is not None:
                byte=load(r['r0']+6,1)
            else:
                if r['r0']!=0x20031000:raise ValueError('Clock parameter address')
                byte=offset_byte
            r[p[0]]=(byte if byte<128 else byte-256)&MASK
        else:raise ValueError('Early-frame path left qualified instructions: '+op)
        pc=nxt
    raise ValueError('Early-frame execution bound')


def verify():
    placement=analyze();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    elf=Elf32((out/'placement.elf').read_bytes(),'early frame')
    sec=next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')
    table=struct.unpack('<19I',elf.contents(sec));code=decode((out/'placement.disassembly.txt').read_text())
    count=0
    for module,source,div in product(range(26),(0,1<<18),(0,2,65536)):
        value,calls=execute(code,table,module,0,4,source,div)
        mapped={17:16,18:16,20:19,21:19,23:22,24:22,25:10}.get(module,module)
        hz=1024000 if source else 12288000
        early=mapped>=10 or mapped in (2,6,9)
        want=0 if module in (7,8) else hz if early or not div else hz//div
        wanted_calls=[] if module in (7,8) else [('lookup',mapped)]+([] if early else [('divider',div)])
        if value!=want or calls!=wanted_calls:raise ValueError('Low-frame result')
        count+=1
    return {'placement':placement,'decoded_cases':count,'source_admitted':False,
            'limits':['Continuous candidate low-frequency paths only. Lookup and divider bodies modeled; fixed valid descriptor offset and selection values. Not whole-function or hardware proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-low-frame.json').write_text(json.dumps(report,indent=2)+'\n');print('Low-frame cases:',report['decoded_cases'])
