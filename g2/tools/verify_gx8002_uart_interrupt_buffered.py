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
    for pending,rxlen,txlen,available,used,delay in product((2,4,6),(0,1,4,8),(0,1,4,8),(0,1,4,9),(0,12,16),(0,3)):
        base=0x20026a94;device=0xa0100000;rxbuf=0x20060001;txbuf=0x20060102
        d=[0x12340000+i for i in range(32)];d[0]=1;d[1]=device;d[11]=0;d[16]=d[17]=2
        d[24]=rxbuf;d[25]=rxlen;d[29]=txbuf;d[30]=txlen;d[22]=0x10300020;d[27]=0x10300030
        regs={device+off:0 for off in range(0,256,4)};regs.update({address:0x76543210 for address in range(0x20060000,0x20060200,4)})
        regs[device]=0x123456ab;regs[device+4]=0x103;regs[device+8]=pending;regs[device+0x84]=available;regs[device+0x80]=used;regs[device+0xf4]=1<<16
        results=[]
        for code,entry in ((old,0xc804),(new,0x10203278)):
            reads=0
            def read(address,value):
                nonlocal reads
                if address==device+20:
                    reads+=1;return 0 if reads<=delay else 64
                return value
            results.append(execute(code,entry,d,regs,read_hook=read));polls+=reads
        if results[0]!=results[1]:raise ValueError(('Buffered interrupt mismatch',cases,results))
        result,memory,trace=results[0];rxcount=min(rxlen,available) if pending&4 else 0;txcount=min(txlen,16-used) if pending&2 else 0
        if result or memory[base+96]!=rxbuf+rxcount or memory[base+100]!=rxlen-rxcount or memory[base+116]!=txbuf+txcount or memory[base+120]!=txlen-txcount:raise ValueError('Buffered cursor oracle')
        received=[(item[1],item[3]) for item in trace if item[0]=='write' and item[2]==1]
        if received!=[(rxbuf+i,0xab) for i in range(rxcount)]:raise ValueError('Receive byte oracle')
        sent=[item[3] for item in trace if item[0]=='write' and item[1]==device]
        wanted=[(regs[(txbuf+i)&~3]>>(((txbuf+i)&3)*8))&255 for i in range(txcount)]
        if sent!=wanted:raise ValueError('Transmit byte oracle')
        callbacks=[]
        if pending&4 and rxcount==rxlen:callbacks.append(('callback',d[22],1,d[23]))
        if pending&2 and txcount==txlen:callbacks.append(('callback',d[27],1,d[28]))
        if [x for x in trace if x[0]=='callback']!=callbacks:raise ValueError('Buffered completion oracle')
        enable=0x103
        if pending&4 and rxcount==rxlen:enable&=~1
        if pending&2 and txcount==txlen:enable&=~2
        if memory[device+4]!=enable:raise ValueError('Completion interrupt mask oracle')
        poll_values=[x[3] for x in trace if x[0]=='read' and x[1]==device+20]
        if poll_values!=([0]*delay+[64] if pending&2 and txcount==txlen else []):raise ValueError('Drain polling oracle')
        cases+=1
    return {'candidate':candidate,'cases':cases,'poll_reads':polls,'source_admitted':False,'hardware_qualified':False,'limits':['Small bounded buffers and no callback mutation in this corpus. Polling completes immediately or after three empty samples; permanently stalled transmitter and large signed count edge cases not qualified. No hardware execution.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-interrupt-buffered.json').write_text(json.dumps(r,indent=2)+'\n');print('Buffered interrupt cases:',r['cases'],r['poll_reads'])
