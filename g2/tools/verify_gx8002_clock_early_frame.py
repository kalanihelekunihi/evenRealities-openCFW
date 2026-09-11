# SPDX-License-Identifier: MIT
"""Continuous entry-to-return clock frame checks for early-exit paths."""
import json
import struct
from itertools import product
from analyze_gx8002_clock_table_placement import analyze,ROOT,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
SP=0x2002f7fc


def execute(code,table,module,lookup_result,offset_byte):
    r={f'r{i}':(0x81234567+i*0x1020304)&MASK for i in range(32)};r.update(r0=module,r14=SP)
    initial=r.copy();memory={};pc=0x10025210;condition=False;calls=[]
    def load(address):
        if address not in memory:raise ValueError('Early-frame unmapped read')
        return memory[address]
    for _ in range(80):
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
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b)&MASK
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','bf','br'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op=='bnez':
            if r[p[0]]:nxt=int(p[1],0)
        elif op=='ldr.w':
            if args!='r3, (r2, r3 << 2)' or r['r2']!=0x10025460 or r['r3']>=19:raise ValueError('Early-frame switch')
            r['r3']=table[r['r3']]
        elif op=='jmp':nxt=r[args]
        elif op=='bsr':
            if int(args,0)!=0x10024a44 or r['r1']!=SP-36:raise ValueError('Early-frame lookup ABI')
            calls.append(r['r0']);memory[r['r1']]=0x20031000
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=lookup_result
        elif op=='ld.w':
            if args!='r0, (r14, 0x0)':raise ValueError('Early-frame stack read')
            r['r0']=load(r['r14'])
        elif op=='ld.bs':
            if args!='r2, (r0, 0x6)' or r['r0']!=0x20031000:raise ValueError('Early-frame parameter')
            r['r2']=(offset_byte if offset_byte<128 else offset_byte-256)&MASK
        else:raise ValueError('Early-frame path left qualified instructions: '+op)
        pc=nxt
    raise ValueError('Early-frame execution bound')


def verify():
    placement=analyze();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    elf=Elf32((out/'placement.elf').read_bytes(),'early frame')
    sec=next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')
    table=struct.unpack('<19I',elf.contents(sec));code=decode((out/'placement.disassembly.txt').read_text())
    count=0
    for module,result in product((*range(256),0x7fffffff,0x80000000,MASK),(0,1,MASK)):
        value,calls=execute(code,table,module,result,255)
        mapped={17:16,18:16,20:19,21:19,23:22,24:22,25:10}.get(module,module)
        if value!=0 or calls!=([] if module in (7,8) else [mapped]):raise ValueError('Early-frame result')
        count+=1
    return {'placement':placement,'decoded_cases':count,'source_admitted':False,
            'limits':['Continuous candidate frame for immediate-zero, failed lookup and -1 offset paths only. Lookup body modeled; successful MMIO paths and hardware not qualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-early-frame.json').write_text(json.dumps(report,indent=2)+'\n');print('Early-frame cases:',report['decoded_cases'])
