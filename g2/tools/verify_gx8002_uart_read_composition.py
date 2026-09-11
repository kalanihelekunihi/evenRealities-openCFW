# SPDX-License-Identifier: MIT
"""Compose stock and rebuilt buffer reads with decoded blocking byte reads."""
import json,subprocess
from itertools import product
from verify_gx8002_uart_read import execute,signed
from verify_gx8002_uart_receive_byte import execute as byte_execute
from build_gx8002_uart_read import build,ROOT
from build_gx8002_uart_receive_byte import build as build_byte
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def verify():
    candidate=build();byte_candidate=build_byte()
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Read composition identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc7ec','--stop-address=0xcb90',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-read/read.disassembly.txt').read_text())
    new.update(decode((ROOT/'build/gx8002-uart-receive-byte/receive_byte.disassembly.txt').read_text()))
    cases=0;stalled=0
    for port,length,delay,stall in product((0,1),(0,1,2,16,0xffffffff,0x80000000),(0,3,32),(None,0,1)):
        count=max(0,signed(length));buffer=0x200a0000;descriptor=0x20026a94+port*128
        values=[(i*37+0x12345600)&0xffffffff for i in range(count)]
        def run(code,entry,helper):
            def receive(pointer,index):
                # Change the peripheral between calls to test fresh descriptor loads.
                device=0xa0100000+index*0x1000
                statuses=[0x40]*delay+([] if index==stall else [3])
                return byte_execute(code,helper,pointer,device,statuses,values[index])
            return execute(code,entry,port,buffer,length,values,helper,receive_hook=receive)
        expected=[];result=count
        for i,value in enumerate(values):
            device=0xa0100000+i*0x1000
            expected.extend([('receive',descriptor),('read',descriptor+4,device)])
            expected.extend([('read',device+20,0x40)]*delay)
            if i==stall:result=None;stalled+=1;break
            expected.extend([('read',device+20,3),('read',device,value),('write_byte',buffer+i,value&255)])
        a=run(old,0xcb64,0xc7ec);b=run(new,0x102035d8,0x10203260)
        if a!=b or a!=(result,expected):raise ValueError('Nested receive trace/result contract')
        cases+=1
    return {'candidate':candidate,'byte_candidate':byte_candidate,'decoded_cases':cases,'stalled_prefixes':stalled,'source_admitted':False,'hardware_qualified':False,'limits':['Nested decoded calls use separate interpreter frames and modeled MMIO stimuli. Stalled prefixes stop before the next unavailable stimulus, without changing firmware polling behavior. Full firmware integration remains pending.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-read-composition.json').write_text(json.dumps(r,indent=2)+'\n');print('Nested read cases:',r['decoded_cases'],'stalled:',r['stalled_prefixes'])
