# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_uart_receive_byte import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,descriptor,device,statuses,data):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=descriptor
    initial=r.copy();pc=entry;trace=[];reads=0
    for _ in range(10000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op in ('addi','andi'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a&b)&0xffffffff
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Receive byte operand')
            reg,base,off=m.groups();address=(r[base]+int(off,0))&0xffffffff
            if address==descriptor+4:value=device if not trace else device+0x10000
            elif address==device+20:
                if reads==len(statuses):return None,trace
                value=statuses[reads];reads+=1
            elif address==device:value=data
            else:raise ValueError('Unexpected receive byte address')
            r[reg]=value;trace.append(('read',address,value))
        elif op=='bez':
            if r[p[0]]==0:jump=int(p[1],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Receive byte ABI')
            return r['r0'],trace
        else:raise ValueError('Receive byte instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Receive byte instruction bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Receive byte stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0xc7ec','--stop-address=0xc804',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-receive-byte/receive_byte.disassembly.txt').read_text());cases=0
    for port,delay,waiting,ready,data in product((0,1),(0,1,3,32,128),(0,2,64,0xfffffffe),(1,3,0xffffffff,None),(0,255,256,0x12345678,0xffffffff)):
        descriptor=0x20080000+port*128;device=0xa0100000+port*0x1000
        statuses=[waiting]*delay+([] if ready is None else [ready])
        expected=(None if ready is None else data&255,[('read',descriptor+4,device)]+[('read',device+20,x) for x in statuses]+([] if ready is None else [('read',device,data)]))
        a=execute(old,0xc7ec,descriptor,device,statuses,data)
        b=execute(new,0x10203260,descriptor,device,statuses,data)
        if a!=b or a!=expected:raise ValueError('Receive byte trace/result mismatch')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Modeled MMIO and finite stalled prefixes; no hardware or firmware integration qualification. Source retains the stock unbounded wait.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-receive-byte-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Receive byte cases:',r['decoded_cases'])
