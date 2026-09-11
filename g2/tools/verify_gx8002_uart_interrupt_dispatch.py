# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from build_gx8002_uart_interrupt import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_interrupt import execute


def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0xc804','--stop-address=0xc8ec',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-uart-interrupt/interrupt.disassembly.txt').read_text())
    cases=0
    for pending,rxmode,txmode,dma,available,mutation in product(range(16),(0,1,3),(0,1,3),(0,1),(0,7,0xffffffff),(False,True)):
        base=0x20026a94;device=0xa0100000;other=0xa0200000
        d=[0x12340000+i for i in range(32)];d[0]=0;d[1]=device;d[11]=dma;d[16]=rxmode;d[17]=txmode
        d[20]=0x10300000;d[18]=0x10300010
        regs={dev+offset:0xa5a50000+offset for dev in (device,other) for offset in range(0,256,4)}
        regs[device+8]=pending;regs[device+0x84]=available
        regs[device+0x80]=17;regs[device+0xf4]=0x00101234
        regs[other+0x80]=0xffffffff;regs[other+0xf4]=0x00011234
        def mutate(target,memory):
            if mutation and target==d[20]:
                memory[base+4]=other;memory[base]=1;memory[base+17*4]=1
                memory[base+19*4]=0xabcd1234;memory[device+8]=0
        a=execute(old,0xc804,d,regs,mutate);b=execute(new,0x10203278,d,regs,mutate)
        if a!=b:raise ValueError(('Interrupt dispatch mismatch',pending,rxmode,txmode,dma,available,mutation,a,b))
        mem={base+i*4:v for i,v in enumerate(d)};mem.update(regs);trace=[]
        def read(address):
            value=mem[address];trace.append(('read',address,4,value));return value
        def call(target,*args):
            trace.append(('callback',target,*args));mutate(target,mem)
        dev=read(base+4);status=read(dev+8)
        if status&4:
            count=read(dev+0x84);mode=read(base+64)
            if mode==1:
                target=read(base+80);context=read(base+84);port=read(base);call(target,port,count,context)
            else:read(base+44)
        if status&2:
            dev=read(base+4);used=read(dev+128);parameter=read(dev+244)
            count=(((parameter>>16)&255)*16-used)&0xffffffff;mode=read(base+68)
            if mode==1:
                target=read(base+72);context=read(base+76);port=read(base);call(target,port,count,context)
            else:read(base+44)
        if a!=(0,mem,trace):raise ValueError(('Interrupt dispatch oracle',cases))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Decoded dispatch and ready-callback paths only: receive/transmit modes 0, 1 and 3. Callback effects modeled, including descriptor/device changes after receive callback. Buffered mode 2 and transmitter drain loop remain unqualified.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-interrupt-dispatch.json').write_text(json.dumps(r,indent=2)+'\n');print('Interrupt dispatch cases:',r['cases'])
