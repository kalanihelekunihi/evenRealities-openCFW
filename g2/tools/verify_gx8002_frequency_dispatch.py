#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode frequency entry through module lookup or immediate zero return."""
import json,re,struct,subprocess
from link_gx8002_clock_frequency_candidate import link,ROOT,Elf32,IMAGE
from verify_gx8002_memcpy_source import decode
from verify_gx8002_padmux_get import build as build_getter,programs


def expected(module):
    if module in (7,8):return ('return',0)
    return ('lookup',{17:16,18:16,20:19,21:19,23:22,24:22,25:10}.get(module,module))


def execute(code,entry,module,table,table_address,delta):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=module,r14=0x2002f7fc)
    pc=entry;condition=False
    for _ in range(35):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4-r5, r15':raise ValueError('Dispatch frame')
            r['r14']-=12
        elif op=='pop':return ('return',r['r0'])
        elif op=='movi' or op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b)&0xffffffff
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op=='ldr.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 2\)',args)
            if not m:raise ValueError('Dispatch table operand')
            reg,base,index=m.groups();offset=r[base]+4*r[index]-table_address
            if offset<0 or offset+4>len(table) or offset%4:raise ValueError('Dispatch table range')
            r[reg]=struct.unpack_from('<I',table,offset)[0]
        elif op=='jmp':nxt=r[args]-delta
        elif op=='bsr':
            if int(args,0)+delta!=0x10024a44:raise ValueError('Dispatch lookup target')
            return ('lookup',r['r0'])
        else:raise ValueError('Unhandled dispatch instruction '+op)
        pc=nxt
    raise ValueError('Dispatch bound')


def verify():
    candidate=link();build_getter();programs();out=ROOT/'build/gx8002-clock-frequency'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x17224','--stop-address=0x173e0',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((out/'frequency-analysis.disassembly.txt').read_text());elf=Elf32((out/'frequency-analysis.elf').read_bytes(),'frequency')
    table=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency'))
    stock=IMAGE.read_bytes();count=0
    for module in (*range(256),0x7fffffff,0x80000000,0xffffffff):
        if execute(old,0x17224,module,stock[0x17474:0x174c0],0x10025460,0x1000dfec)!=expected(module) or execute(new,0x10025210,module,table,0x11000000,0)!=expected(module):raise ValueError('Frequency dispatch mismatch')
        count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,'limits':['Dispatch only; frequency arithmetic, MMIO and whole-function ABI are not qualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-frequency-dispatch-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded dispatch cases:',report['decoded_cases'])
