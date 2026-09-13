# SPDX-License-Identifier: MIT
"""Decoded UART-message selector and send-start state transitions."""
import json,re,subprocess
from itertools import product
from build_gx8002_uart_message_body import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
BASE=0x2002e050
MASK=0xffffffff

def execute(code,entry,port,packet,available,memory):
    memory=memory.copy();r={f'r{i}':0xabc00000+i for i in range(32)};r['r14']=0x20070000;r['r0']=port;r['r1']=packet;r['r2']=available;initial=r.copy();saved=None;events=[];pc=entry;condition=False
    frame='r4-r10, r15' if entry<0x100000 else 'r4-r9, r15'
    regs=tuple('r'+str(i) for i in range(4,11 if entry<0x100000 else 10))+('r15',)
    for _ in range(65):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!=frame or saved is not None:raise ValueError('Frame')
            saved={key:r[key] for key in regs};r['r14']-=4*len(regs)
        elif op in ('pop','rts'):
            if op=='pop':
                if args!=frame or saved is None:raise ValueError('Restore')
                r.update(saved);r['r14']+=4*len(regs)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return ('return',r['r0']),memory,events
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op in ('addu','subu','lsli'):
            left=r[p[0] if len(p)==2 else p[1]];right=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(left+right if op=='addu' else left-right if op=='subu' else left<<right)&MASK
        elif op=='min.u32':r[p[0]]=min(r[p[1]],r[p[2]])
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='mvcv':r[p[0]]=int(not condition)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('br','bt','bf'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op in ('ld.w','st.w','ld.b','ldr.w','str.w'):
            if op in ('ldr.w','str.w'):
                reg,base,index,shift=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args).groups();address=(r[base]+(r[index]<<int(shift)))&MASK
            else:
                reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(off,0))&MASK
            if op.startswith('ld'):
                r[reg]=memory[address] if op=='ld.b' else word(memory,address)
            else:
                if any(address+i not in memory for i in range(4)):raise ValueError('Out of bounds write')
                word(memory,address,r[reg]);events.append(('write',address,r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry<0x100000 else 0))&MASK;value=0
            if target==0x10203604:
                return ('uart_write',r['r0'],r['r1'],r['r2']),memory,events
            if target==0x10207ac0:
                value={0:BASE,1:BASE+380}.get(r['r0'],0);events.append(('get',r['r0']))
            elif target==0x10203630:events.append(('restart',r['r0'],r['r1'],r['r2']))
            else:raise ValueError('Target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=value
        else:raise ValueError(('Opcode',op))
        pc=nxt
    raise ValueError('Bound')

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x110c4','--stop-address=0x111dc',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-uart-message-body/buffers.disassembly.txt').read_text());cases=0
    for port,count,total,space,flags in product((0,1),(0,1,15,16,32,0xffffffff),(0,1,16,33,64,0xffffffff),(0,1,16,32,0xffffffff),(0,1,255)):
        context=BASE+port*380;packet=0x20040000;available=0x20041000;memory={BASE+i:(i*37)&255 for i in range(800)};memory.update({packet+i:0 for i in range(32)});memory.update({available+i:0 for i in range(4)})
        word(memory,0x2002e348+port*4,count);word(memory,0x2002e350+port*4,total);word(memory,packet+24,total);word(memory,packet+16,0xfffffff0);word(memory,available,space);memory[context+67]=flags
        a=execute(old,0x110c4,port,packet,available,memory);b=execute(new,0x10207b38,port,packet,available,memory)
        expected_memory=memory.copy();expected_events=[]
        if count==0:
            word(expected_memory,0x2002e350+port*4,total);expected_events.append(('write',0x2002e350+port*4,total))
        if count==total:
            word(expected_memory,0x2002e348+port*4,0);word(expected_memory,context+372,2 if flags else 3)
            expected_events.extend([('write',0x2002e348+port*4,0),('get',port),('write',context+372,2 if flags else 3),('restart',port,0x10207f08,0)])
            endpoint=('return',1)
        elif not space:
            expected_events.append(('restart',port,0x10207f08,0));endpoint=('return',MASK)
        else:endpoint=('uart_write',port,(0xfffffff0+count)&MASK,min(space,(total-count)&MASK))
        if a!=b or a!=(endpoint,expected_memory,expected_events):raise ValueError(('Prefix',port,count,total,space,flags,a,b))
        cases+=1
    return {'candidate':candidate,'decoded_prefix_cases':cases,'source_admitted':False,'limits':['Entry through return or first UART write only. Complete send scheduling, aliasing and helper mutation remain pending. Valid ports, nonnull packet and available pointers; boundaries include unsigned arithmetic wrap.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-send-body-prefix.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_prefix_cases'])
