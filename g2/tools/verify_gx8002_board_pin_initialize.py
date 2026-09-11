# SPDX-License-Identifier: MIT
"""Decoded board initializer table access/call order and completion flag."""
import json,re,subprocess
from itertools import product
from build_gx8002_board_pin_initialize_candidate import ROOT,build
from verify_gx8002_memcpy_source import decode
from compare_gx8002_uart_putc import register_list
MASK=0xffffffff
ADDRESS=0x102068a0
TABLE=0x1020ad30


def expected(table,errors,returns):
    trace=[('init',TABLE,13)]
    for i,(pin,function) in enumerate(table):
        trace.extend([('read',TABLE+2*i,pin),('read',TABLE+2*i+1,function),('check',pin,function)])
        if errors&(1<<i):trace.append(('printf',0x1020ad97,pin))
        if function==int(pin!=2):trace.append(('direction',pin,0))
    trace.append(('setup',))
    if returns:trace.append(('write',0x20027b4c,1))
    return ('returned' if returns else 'setup-nonreturn'),trace


def execute(code,entry,table,errors,returns=True,setup_hook=None,direction_hook=None,printf_hook=None,check_hook=None,init_hook=None):
    memory={TABLE+2*i+j:v for i,pair in enumerate(table) for j,v in enumerate(pair)}
    r={f'r{i}':(0x91730000+i*0x10203)&MASK for i in range(32)}
    r['r14']=0x2002f7fc;initial=r.copy();pc=entry;saved=None;trace=[];condition=False;index=0
    for _ in range(1000):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if saved is not None:raise ValueError('Initializer nested frame')
            names=register_list(args);saved={name:r[name] for name in names};r['r14']-=4*len(names)
        elif op=='pop':
            if saved is None or set(register_list(args))!=set(saved):raise ValueError('Initializer restore')
            r.update(saved);r['r14']+=4*len(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Initializer ABI')
            return 'returned',trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op in ('addu','addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]]
            b=r[p[-1]] if op=='addu' else int(p[-1],0)
            r[p[0]]=(a-b if op=='subi' else a+b)&MASK
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='bt':
            if condition:nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op in ('ld.b','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Initializer memory operand')
            reg,base,offset=m.groups();address=(r[base]+int(offset,0))&MASK
            if op=='ld.b':
                if address not in memory:raise ValueError('Initializer table extent')
                r[reg]=memory[address];trace.append(('read',address,r[reg]))
            else:
                if address!=0x20027b4c:raise ValueError('Initializer flag address')
                trace.append(('write',address,r[reg]))
        elif op=='bsr':
            target=int(args,0)
            if entry==0xfe2c:target=(target+0x101f6a74)&MASK
            value=0x8a51
            if target==0x10206630:
                trace.append(('init',r['r0'],r['r1']))
                if init_hook is not None:value=init_hook(r['r0'],r['r1'])
            elif target==0x102065b8:
                trace.append(('check',r['r0'],r['r1']));value=MASK if errors&(1<<index) else 0;index+=1
                if check_hook is not None:value=check_hook(r['r0'],r['r1'])
            elif target==0x10206c24:
                trace.append(('printf',r['r0'],r['r1']))
                if printf_hook is not None:value=printf_hook(r['r0'],r['r1'])
            elif target==0x10205f24:
                trace.append(('direction',r['r0'],r['r1']))
                if direction_hook is not None:value=direction_hook(r['r0'],r['r1'])
            elif target==0x1020681c:
                trace.append(('setup',))
                if setup_hook is not None:returns=setup_hook()
                if not returns:return 'setup-nonreturn',trace
            else:raise ValueError('Initializer helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xa1790000+i
            r['r0']=value
        else:raise ValueError('Initializer instruction '+op)
        pc=nxt
    raise ValueError('Initializer bound')


def programs():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');out=ROOT/'build/gx8002-board'
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xfe2c','--stop-address=0xfe94',str(out/'padmux-get-stock.elf')],text=True))
    new=decode((out/'board-pin-initialize-candidate.disassembly.txt').read_text())
    return old,new


def verify():
    candidate=build();old,new=programs();count=0
    tables=[[(p,int(p!=2)) for p in range(13)],[(p,3) for p in range(13)],[(2,0)]*13,[(255,255)]*13]
    for table,errors,returns in product(tables,(0,8191,*[1<<i for i in range(13)]),(False,True)):
        for code,entry in ((old,0xfe2c),(new,ADDRESS)):
            if execute(code,entry,table,errors,returns)!=expected(table,errors,returns):raise ValueError('Initializer mismatch')
            count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Finite table/call traces with modeled helper returns and setup nonreturn. Separate saved-register frame; no nested helper or physical hardware proof.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-board-pin-initialize-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Initializer decoded cases:',report['decoded_cases'])
