# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from analyze_gx8002_upstream_objects import ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_body_complete_stock import execute as stock
from execute_gx8002_uart_body_complete_source import execute as source


def verify():
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x112b8','--stop-address=0x11458',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-body-probe/body.linked.disassembly.txt').read_text());cases=0
    for port,flags,length,status in product((0,1),(0,1),(4,20,256),(0,1,0xffffffff)):
        ctx=0x20040000;packet=ctx+28;counter=0x2002e358+4*port
        memory={ctx+i:0xa5 for i in range(380)}
        def put(addr,value,n=4):
            for i in range(n):memory[addr+i]=(value>>(8*i))&255
        def get(addr):return sum(memory[addr+i]<<(8*i) for i in range(4))
        put(ctx+8,port);put(packet+7,flags,1);put(packet+8,length,2);put(ctx+368,2);put(counter,length-(4 if flags else 0))
        expected_packet=bytearray(memory[packet+i] for i in range(32));expected_packet[20]=port;expected_packet[24:28]=length.to_bytes(4,'little')
        other=memory.copy()
        _,sr,st=stock(old,memory,dict(r0=0x2002e050+port*4,r5=ctx,r6=port,r11=packet),helper_result=status)
        _,nr,nt=source(new,other,dict(r0=ctx,r4=packet,r5=port,r8=0x2002e358,r9=port,r10=ctx),helper_result=status)
        calls=[('restart',port,0x10208098,0)]+([] if flags else [('queue',expected_packet.hex())])
        if [x for x in st if isinstance(x[0],str)]!=calls or [x for x in nt if isinstance(x[0],str)]!=calls:raise ValueError('Completion calls')
        if memory!=other or sr['r4']!=0 or nr['r0']!=0 or get(counter)!=0 or get(ctx+368)!=(3 if flags else 0):raise ValueError('Completion state')
        if not flags and (get(packet)!=0 or get(packet+24)!=0):raise ValueError('Completion cleanup')
        cases+=1
    return {'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Body count already equals expected size at entry. Restart/queue helpers modeled; whole-body execution and concurrent updates pending.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-body-complete.json').write_text(json.dumps(r,indent=2)+'\n');print('Body completion cases:',r['decoded_cases'])
