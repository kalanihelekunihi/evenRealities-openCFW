# SPDX-License-Identifier: MIT
"""Compose decoded buffer writes with the recovered polled transmitter."""
import json,subprocess
from itertools import product
from verify_gx8002_uart_write import execute,signed
from compare_gx8002_uart_transmit import execute as transmit
from build_gx8002_uart_write import build,ROOT
from link_gx8002_uart_console import build as build_console
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def verify():
    candidate=build();console=build_console()
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Write composition identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc7d8','--stop-address=0xcbbc',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-write/write.disassembly.txt').read_text())
    new.update(decode(subprocess.check_output([pre,'-d','--section=.text.open_cfw_gx8002_uart_transmit',str(ROOT/'build/gx8002-uart-console/console.elf')],text=True)))
    cases=0;stalled=0
    for port,length,delay,stall in product((0,1),(0,1,2,16,0xffffffff,0x80000000),(0,3,32),(None,0,1)):
        count=max(0,signed(length));buffer=0x200a0000;descriptor=0x20026a94+port*128
        values=[(i*37+127)&255 for i in range(count)]
        def run(code,entry,helper):
            def send(pointer,value,index):
                device=0xa0100000+index*0x1000
                status,trace=transmit(code,helper,pointer,device,value,[0xffffffdf]*delay+([] if index==stall else [33]))
                return status=='returned',trace
            return execute(code,entry,port,buffer,length,values,helper,transmit_hook=send)
        expected=[];result=count
        for i,value in enumerate(values):
            device=0xa0100000+i*0x1000
            expected.extend([('read_byte',buffer+i,value),('transmit',descriptor,value),('read',descriptor+4,4,device)])
            expected.extend([('read',device+20,4,0xffffffdf)]*delay)
            if i==stall:result=None;stalled+=1;break
            expected.extend([('read',device+20,4,33),('write',device,4,value)])
        a=run(old,0xcb90,0xc7d8);b=run(new,0x10203604,0x1020324c)
        if a!=b or a!=(result,expected):raise ValueError('Nested transmit trace/result contract')
        cases+=1
    return {'candidate':candidate,'console':console,'decoded_cases':cases,'stalled_prefixes':stalled,'source_admitted':False,'hardware_qualified':False,'limits':['Separate decoded interpreter frames with modeled MMIO; stalled prefixes stop at unavailable stimulus. Physical timing and complete firmware integration remain unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-write-composition.json').write_text(json.dumps(r,indent=2)+'\n');print('Nested write cases:',r['decoded_cases'],'stalled:',r['stalled_prefixes'])
