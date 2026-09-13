# SPDX-License-Identifier: MIT
"""Decoded power initialization, callback mutation, memory ordering and ABI."""
import json,re,subprocess
from itertools import product
from build_gx8002_power_suspend import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
BASE=0x2002dfbc
MASK=0xffffffff

def word(memory,address,value=None):
    if value is None:return sum(memory[address+i]<<(8*i) for i in range(4))
    for i in range(4):memory[address+i]=(value>>(8*i))&255

def mutate(memory,policy,call):
    if policy==1:word(memory,BASE+8,0)
    if policy==2:word(memory,BASE+8,8)
    if policy==3:word(memory,BASE+8,call+1)
    if policy==4:
        for i in range(call+1,8):
            word(memory,BASE+16+i*8,0x10210000+i*4)
            word(memory,BASE+20+i*8,0xff000000+i)

def execute(code,entry,kind,memory,policy,result,irq,busy,changed,padding=0xa5):
    memory=memory.copy();r={f'r{i}':0xabc00000+i for i in range(32)};r['r14']=0x20070000;r['r0']=kind;initial=r.copy();saved=None;events=[];pc=entry;condition=False;calls=0;polls=0
    stack=0x20070000-36
    memory.update({stack+i:padding for i in range(12)})
    for _ in range(400):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4-r8, r15' or saved is not None:raise ValueError('Frame')
            saved={key:r[key] for key in ('r4','r5','r6','r7','r8','r15')};r['r14']-=24
        elif op=='pop':
            if args!='r4-r8, r15' or saved is None:raise ValueError('Restore')
            r.update(saved);r['r14']+=24
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],memory,events
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('br','bt','bf'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op in ('ld.w','st.w','st.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(off,0))&MASK
            if op=='ld.w':
                r[reg]=word(memory,address)
                if address<stack:events.append(('read',address,r[reg]))
            else:
                size=1 if op=='st.b' else 4
                if not stack<=address<=stack+12-size:raise ValueError('Unexpected write')
                if size==1:memory[address]=r[reg]&255
                else:word(memory,address,r[reg])
        elif op in ('bsr','jsr'):
            target=((int(args,0)+(0x101f6a74 if entry<0x100000 else 0))&MASK) if op=='bsr' else r[args]
            if op=='jsr':
                events.append(('callback',target,r['r0']));mutate(memory,policy,calls);calls+=1;value=result
            elif target==0x10025560:events.append(('irq_save',));value=irq
            elif target==0x1002556c:events.append(('irq_restore',r['r0']));value=result
            elif target==0x10207644:events.append(('audio_suspend',));value=result
            elif target==0x10205e28:
                value=1 if polls<busy else result
                if value==1 and polls>=busy:value=0
                events.append(('snpu_state',value));polls+=1
            elif target==0x10205d40:events.append(('snpu_exit',));value=result
            elif target==0x10025d74:
                command=r['r0'];address=r['r1']
                if command==3:
                    if address!=stack:raise ValueError('Data pointer')
                    events.append(('pmu_mode',word(memory,address)))
                    if changed is not None:word(memory,address,changed)
                elif command==5:
                    if address!=stack+4:raise ValueError('Wakeup pointer')
                    events.append(('pmu_wakeup',memory[address],word(memory,address+4)))
                else:raise ValueError('PMU command')
                value=result
            elif target==0x10025534:events.append(('disable_all',));value=result
            elif target==0x102047b8:events.append(('interrupt',r['r0'],r['r1']));value=result
            elif target==0x10206c24:events.append(('printf',r['r0']));value=result
            elif target==0x100248cc:events.append(('pmu_enable',));value=result
            else:raise ValueError(('Helper target',hex(target)))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=value
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')

def oracle(kind,memory,policy,result,irq,busy,changed,padding=0xa5):
    memory=memory.copy();stack=0x20070000-36;memory.update({stack+i:padding for i in range(12)});events=[('irq_save',)]
    active=word(memory,BASE);events.append(('read',BASE,active))
    if active:
        events.append(('irq_restore',irq));return MASK,memory,events
    i=0
    while True:
        count=word(memory,BASE+8);events.append(('read',BASE+8,count))
        if i>=count:break
        address=BASE+16+i*8;callback=word(memory,address);private=word(memory,address+4)
        events.extend([('read',address,callback),('read',address+4,private),('callback',callback,private)])
        mutate(memory,policy,i);i+=1
    events.extend([('irq_restore',irq),('audio_suspend',)])
    events.extend([('snpu_state',1)]*busy);events.extend([('snpu_state',0 if result==1 else result),('snpu_exit',)])
    word(memory,stack,kind);memory[stack+4]=1;word(memory,stack+8,0x10023500)
    events.append(('pmu_mode',kind))
    if changed is not None:word(memory,stack,changed)
    events.extend([('pmu_wakeup',1,0x10023500),('disable_all',)])
    if word(memory,stack)&4:events.append(('interrupt',0x10000,1))
    events.extend([('printf',0x1020ae80),('pmu_enable',)])
    return 0,memory,events

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10d94','--stop-address=0x10e30',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-power-suspend/buffers.disassembly.txt').read_text());cases=0
    for active,count,policy,kind,busy,changed in product((0,1,0x80000000),range(9),range(5),(0,4,0xffffffff),(0,1,5),(None,0,4)):
        result=(0,1,0x80000000,0xffffffff)[cases%4];irq=(0,1,0x80000000,0xffffffff)[(cases//4)%4]
        memory={BASE+i:(i*37+cases)&255 for i in range(-16,160)};word(memory,BASE,active);word(memory,BASE+8,count)
        for i in range(8):word(memory,BASE+16+i*8,0x10200000+i*4);word(memory,BASE+20+i*8,(cases*0x80000000+i)&MASK)
        expected=oracle(kind,memory,policy,result,irq,busy,changed,cases&255)
        for code,base in ((old,0),(new,0x101f6a74)):
            actual=execute(code,0x10d94+base,kind,memory,policy,result,irq,busy,changed,cases&255)
            if actual!=expected:raise ValueError(('Suspend',active,count,policy,kind,busy,changed,actual,expected))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Ordered registry reads, callbacks, IRQ restoration, bounded SNPU busy polling, PMU arguments and data mutation, stack bytes and ABI checked. Helpers modeled; all256 wakeup padding byte values covered, physical suspend and asynchronous mutation unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-power-suspend-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
