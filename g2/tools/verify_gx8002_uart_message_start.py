# SPDX-License-Identifier: MIT
"""Decoded UART-message selector and send-start state transitions."""
import json,re,subprocess
from itertools import product
from build_gx8002_uart_message_start import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
BASE=0x2002e050
MASK=0xffffffff

def execute(code,entry,port,memory,empty,result,mutation):
    memory=memory.copy();r={f'r{i}':0xabc00000+i for i in range(32)};r['r14']=0x20070000;r['r0']=port;initial=r.copy();saved=None;events=[];pc=entry;condition=False
    for _ in range(55):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4-r7, r15' or saved is not None:raise ValueError('Frame')
            saved={key:r[key] for key in ('r4','r5','r6','r7','r15')};r['r14']-=20
        elif op in ('pop','rts'):
            if op=='pop':
                if args!='r4-r7, r15' or saved is None:raise ValueError('Restore')
                r.update(saved);r['r14']+=20
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],memory,events
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='br':nxt=int(args,0)
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0)
            if op=='ld.w':r[reg]=word(memory,address);events.append(('read',address,r[reg]))
            else:
                if address not in (BASE+port*380+24,BASE+port*380+372):raise ValueError('State write')
                word(memory,address,r[reg]);events.append(('write',address,r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry<0x100000 else 0))&MASK;value=result
            if target==0x10207ac0:
                value,_,nested=execute(code,0x1104c if entry<0x100000 else target,r['r0'],memory,empty,result,mutation)
                if nested:raise ValueError('Selector effects')
                events.append(('get',port,value))
            else:
                names={0x10206ffc:('empty',1),0x10206fb0:('queue_get',2),0x102077a8:('lock',1),0x10203664:('stop',1),0x10203630:('start',3)}
                name,count=names[target];events.append((name,*(r[f'r{i}'] for i in range(count))))
                if name=='empty':value=empty
                if name==mutation:
                    address=BASE+port*380
                    for i in range(380):memory[address+i]^=(i*13+71)&255
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=value
        else:raise ValueError(('Opcode',op))
        pc=nxt
    raise ValueError('Bound')

def oracle(port,memory,empty,mutation):
    memory=memory.copy();address=BASE+port*380 if port<2 else 0;events=[('get',port,address)]
    if not address:return MASK,memory,events
    def call(name,*args):
        events.append((name,*args))
        if name==mutation:
            for i in range(380):memory[address+i]^=(i*13+71)&255
    def write(offset,value):word(memory,address+offset,value);events.append(('write',address+offset,value))
    def read(offset):
        value=word(memory,address+offset);events.append(('read',address+offset,value));return value
    call('empty',address+348)
    if empty:write(24,0);call('stop',port);return MASK,memory,events
    write(24,1);call('queue_get',address+348,address+60);write(372,0)
    call('lock',read(376));call('start',read(8),0x10207f08,0)
    return 0,memory,events

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x1104c','--stop-address=0x110c4',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-uart-message-start/buffers.disassembly.txt').read_text());cases=0
    for port,empty,result,mutation in product((*range(256),256,257,0x80000000,0xffffffff),(0,1,0xffffffff),(0,1,0x80000000,0xffffffff),(None,'empty','queue_get','lock','start','stop')):
        memory={BASE+i:(i*37+cases)&255 for i in range(-16,776)};expected=oracle(port,memory,empty,mutation)
        for code,base in ((old,0),(new,0x101f6a74)):
            selector=execute(code,0x1104c+base,port,memory,empty,result,mutation)
            if selector!=(BASE+port*380 if port<2 else 0,memory,[]):raise ValueError('Selector')
            if execute(code,0x11068+base,port,memory,empty,result,mutation)!=expected:raise ValueError(('Send',port,empty,result,mutation))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Decoded nested selector, full guarded context memory, ordered helper arguments/state accesses and ABI match independent oracle. Helpers can mutate all380 context bytes; valid ports0/1 and invalid byte/high-bit inputs tested. Helpers modeled; UART hardware and concurrency unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-message-start-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
