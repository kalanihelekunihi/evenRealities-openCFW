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
    new=decode((ROOT/'build/gx8002-uart-interrupt/interrupt.disassembly.txt').read_text());cases=0;polls=0
    for txlen,used,mode,dma in product((0,1,4,8),(0,12,16),(0,1,2,3),(0,1)):
        base=0x20026a94;device=0xa0100000;other=0xa0200000;rxbuf=0x20060001;txbuf=0x20060102
        d=[0x12340000+i for i in range(32)];d[0]=1;d[1]=device;d[11]=0;d[16]=d[17]=2
        d[24]=rxbuf;d[25]=1;d[29]=txbuf;d[30]=99;d[22]=0x10300020;d[27]=0x10300030;d[18]=0x10300010
        regs={dev+off:0 for dev in (device,other) for off in range(0,256,4)}
        regs.update({address:0x76543210 for address in range(0x20060000,0x20060200,4)})
        regs[device]=0xab;regs[device+4]=3;regs[device+8]=6;regs[device+0x84]=1
        regs[other+4]=3;regs[other+20]=64;regs[other+0x80]=used;regs[other+0xf4]=1<<16
        def mutate(target,memory):
            if target==d[22]:
                memory[base]=9;memory[base+4]=other;memory[base+44]=dma;memory[base+68]=mode
                memory[base+116]=txbuf+1;memory[base+120]=txlen
                memory[base+108]=0x10300040;memory[base+112]=0xabc12345
                memory[device+8]=0
        a=execute(old,0xc804,d,regs,mutate);b=execute(new,0x10203278,d,regs,mutate)
        if a!=b:raise ValueError(('Buffered callback mutation mismatch',cases))
        result,memory,trace=a;count=min(txlen,16-used) if mode==2 and not dma else 0
        if result or memory[base+116]!=txbuf+1+count or memory[base+120]!=txlen-count:raise ValueError('Mutated cursor oracle')
        writes=[(x[1],x[3]) for x in trace if x[0]=='write' and x[1] in (device,other)]
        wanted=[(other,(regs[(txbuf+1+i)&~3]>>(((txbuf+1+i)&3)*8))&255) for i in range(count)]
        if writes!=wanted:raise ValueError('Mutated transmit oracle')
        callbacks=[('callback',d[22],1,d[23])]
        if mode==1:callbacks.append(('callback',d[18],9,16-used,d[19]))
        if mode==2 and not dma and count==txlen:callbacks.append(('callback',0x10300040,9,0xabc12345))
        if [x for x in trace if x[0]=='callback']!=callbacks:raise ValueError('Mutated callback oracle')
        if memory[device+4]!=2 or memory[other+4]!=(1 if mode==2 and not dma and count==txlen else 3):raise ValueError('Mutated interrupt mask oracle')
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Receive completion callback mutates device, mode, DMA state, transmit buffer/length, completion callback/context and port. Callback bodies are modeled; no hardware or concurrency qualification.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-interrupt-mutation.json').write_text(json.dumps(r,indent=2)+'\n');print('Buffered callback mutation cases:',r['cases'])
