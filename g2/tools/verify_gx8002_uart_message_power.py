# SPDX-License-Identifier: MIT
"""Decoded two-port suspend/resume ordering with mutable contexts."""
import json,re,subprocess
from itertools import product
from build_gx8002_uart_message_power import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
BASE=0x2002e050

def mutate(memory,name,policy):
    if name==policy:
        for i in range(760):memory[BASE+i]^=(i*13+71)&255

def execute(code,entry,memory,present,fail,policy,result):
    memory=memory.copy();r={f'r{i}':0xabc00000+i for i in range(32)};r['r14']=0x20070000;initial=r.copy();saved=None;events=[];pc=entry;condition=False;selected=0
    count=3 if entry==0x11228 else 2;frame='r4-r6, r15' if count==3 else 'r4-r5, r15';regs=tuple('r'+str(i) for i in range(4,4+count))+('r15',)
    for _ in range(100):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!=frame or saved is not None:raise ValueError('Frame')
            saved={key:r[key] for key in regs};r['r14']-=4*len(regs)
        elif op=='pop':
            if args!=frame or saved is None:raise ValueError('Restore')
            r.update(saved);r['r14']+=4*len(regs)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],memory,events
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op in ('addi','subi'):r[p[0]]=(r[p[0]]+(1 if op=='addi' else -1)*int(p[1],0))&0xffffffff
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('br','bt'):
            if op=='br' or condition:nxt=int(args,0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op=='ld.w':
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0);r[reg]=word(memory,address);events.append(('read',address,r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry<0x100000 else 0))&0xffffffff;value=result
            if target==0x10207ac0:
                selected=r['r0'];events.append(('get',selected));value=BASE+380*selected if present&(1<<selected) else 0
            else:
                name,nargs={0x102036e8:('stop_send',1),0x10203704:('stop_recv',1),0x10203530:('init',2),0x1020368c:('start',3)}[target]
                events.append((name,*(r[f'r{i}'] for i in range(nargs))));mutate(memory,name,policy)
                if name=='init':value=result if fail&(1<<selected) else 0
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=value
        else:raise ValueError(('Opcode',op))
        pc=nxt
    raise ValueError('Bound')

def oracle(memory,resume,present,fail,policy,result):
    memory=memory.copy();events=[]
    def read(address):
        value=word(memory,address);events.append(('read',address,value));return value
    def call(name,*args):events.append((name,*args));mutate(memory,name,policy)
    for port in range(2):
        events.append(('get',port))
        if not present&(1<<port):continue
        address=BASE+380*port
        if resume and read(address+12)!=1:continue
        call('stop_send',read(address+8));call('stop_recv',read(address+8))
        if resume:
            baud=read(address+16);uart=read(address+8);call('init',uart,baud)
            if fail&(1<<port) and result:return 0xffffffff,memory,events
            call('start',read(address+8),0x10208098,0)
    return 0,memory,events

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11200','--stop-address=0x11278',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-uart-message-power/buffers.disassembly.txt').read_text());cases=0
    for first,second,present,fail,policy,result in product((0,1,2,0xffffffff),(0,1,2,0xffffffff),range(4),range(4),(None,'stop_send','stop_recv','init','start'),(0,1,0x80000000,0xffffffff)):
        memory={BASE+i:(i*37+cases)&255 for i in range(-16,776)};word(memory,BASE+12,first);word(memory,BASE+392,second)
        for resume,offset in ((False,0x11200),(True,0x11228)):
            expected=oracle(memory,resume,present,fail,policy,result)
            for code,base in ((old,0),(new,0x101f6a74)):
                if execute(code,offset+base,memory,present,fail,policy,result)!=expected:raise ValueError(('Power',resume,first,second,present,fail,policy,result))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Independent ordered read/call oracle, both complete contexts and guards, early init failure and ABI verified. Modeled lookup includes unavailable contexts; helpers mutate both contexts between rereads. Physical UART suspend/resume and asynchronous concurrency unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-message-power-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
