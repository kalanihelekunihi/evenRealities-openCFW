# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_uart_transmit_control import build,ROOT
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def execute(code,entry,kind,port,callback,private,word,token,irq_hook=None,descriptor_base=0x20026a94,save_entry=0x10025560,restore_entry=0x1002556c,initial_memory=None):
    descriptor=(descriptor_base+(port<<7))&0xffffffff;base=0xa0000000+port*0x1000
    memory={descriptor+4:base,descriptor+68:7,descriptor+72:0x1234,descriptor+76:0x5678,base+4:word}
    if initial_memory is not None:memory=dict(initial_memory)
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=port,r1=callback,r2=private,r14=0x2002f000)
    initial=r.copy();trace=[];pc=entry;saved=None;regs=['r4','r15'] if kind=='start' else ['r4','r5','r15']
    for _ in range(60):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!=('r4, r15' if kind=='start' else 'r4-r5, r15') or saved is not None:raise ValueError('Transmit frame')
            saved=[r[x] for x in regs];r['r14']-=len(regs)*4
        elif op=='pop':
            if args!=('r4, r15' if kind=='start' else 'r4-r5, r15') or saved is None:raise ValueError('Transmit restore')
            for reg,value in zip(regs,saved):r[reg]=value
            r['r14']+=len(regs)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Transmit ABI')
            return r['r0'],trace,memory
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','subi','lsli','ori','andni'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op=='addu' else a-b if op=='subi' else a<<b if op=='lsli' else a|b if op=='ori' else a&~b)&0xffffffff
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='bez':
            if r[p[0]]==0:jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Transmit memory operand')
            reg,base_reg,off=m.groups();addr=(r[base_reg]+int(off,0))&0xffffffff
            if addr not in memory:raise ValueError('Transmit memory address')
            if op=='ld.w':r[reg]=memory[addr];trace.append(('read',addr,r[reg]))
            else:memory[addr]=r[reg];trace.append(('write',addr,r[reg]))
        elif op=='bsr':
            target=int(args,0)
            save=target in (0xffe2eaec,save_entry)
            if not save and target not in (0xffe2eaf8,restore_entry):raise ValueError('Transmit IRQ target')
            if irq_hook is not None:
                result=irq_hook(save,r['r0'])
                if save and result!=token:raise ValueError('Transmit decoded IRQ token')
            if save:trace.append(('irq_save',))
            else:
                if r['r0']!=token:raise ValueError('Transmit IRQ token lost')
                trace.append(('irq_restore',token))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=token if save else 0xffffffff
        else:raise ValueError('Transmit instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Transmit instruction bound')


def expected(kind,port,callback,private,word,token):
    """Independent descriptor and interrupt-enable contract for valid ports."""
    descriptor=0x20026a94+port*128;base=0xa0000000+port*0x1000
    memory={descriptor+4:base,descriptor+68:7,descriptor+72:0x1234,descriptor+76:0x5678,base+4:word}
    if kind=='start' and callback==0:return 0xffffffff,[],memory
    writes=[(descriptor+68,1),(descriptor+72,callback),(descriptor+76,private)] if kind=='start' else [(descriptor+72,0),(descriptor+76,0)]
    trace=[]
    for address,value in writes:
        memory[address]=value;trace.append(('write',address,value))
    enabled=word|2 if kind=='start' else word&0xfffffffd
    trace += [('irq_save',),('read',descriptor+4,base),('read',base+4,word),('write',base+4,enabled),('irq_restore',token)]
    memory[base+4]=enabled
    return 0,trace,memory


def verify():
    candidate=build()
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Transmit stock wrapper identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');cases=0
    for kind,offset,size in (('start',0xcbbc,52),('stop',0xcbf0,40)):
        old=decode(subprocess.check_output([pre,'-D','--start-address='+hex(offset),'--stop-address='+hex(offset+size),str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
        new=decode((ROOT/'build/gx8002-uart-transmit-control'/(kind+'.disassembly.txt')).read_text())
        for port,callback,private,word,token in product((0,1),(0,0x10208098),(0,0x12345678),(0,1,0xffffffff),(0,1,0x80000000,0xffffffff)):
            a=execute(old,offset,kind,port,callback,private,word,token)
            b=execute(new,offset+0x101f6a74,kind,port,callback,private,word,token)
            if a!=b:raise ValueError('Transmit control stock/source mismatch')
            if a!=expected(kind,port,callback,private,word,token):raise ValueError('Transmit control independent contract mismatch')
            if a[0]!=(0xffffffff if kind=='start' and not callback else 0):raise ValueError('Transmit result')
            cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Finite descriptor/MMIO and IRQ-token cases, exact trace comparison. IRQ helpers modeled; physical UART effects unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-transmit-control-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Transmit control cases:',r['decoded_cases'])
