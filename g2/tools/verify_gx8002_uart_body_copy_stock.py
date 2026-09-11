# SPDX-License-Identifier: MIT
"""Stock body byte-copy and completion paths, before async scheduling."""
import json,subprocess
from itertools import product
from analyze_gx8002_upstream_objects import ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_body_copy_stock import execute


def verify():
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x113b0','--stop-address=0x11458',str(wrapper)],text=True));cases=0
    for port,flags,size,count,available in product((0,1),(0,1),(1,16,33,80),(0,1,15),(1,8,32,64)):
        if count>=size:continue
        ctx=0x20040000;packet=0x20041000;pointer=0x20042000;length=pointer+4;src=0x20050000;dest=0x20060000
        memory={dest+i:0xcc for i in range(128)};memory.update({src+i:(i*17+3)&255 for i in range(available)})
        def put(addr,value,n=4):
            for i in range(n):memory[addr+i]=(value>>(8*i))&255
        def get(addr):return sum(memory[addr+i]<<(8*i) for i in range(4))
        put(packet+16,dest);put(packet+7,flags,1);put(pointer,src);put(length,available);put(ctx+368,2);put(0x2002e358+port*4,count)
        regs=dict(r1=count,r2=size,r3=src,r5=ctx,r7=0x2002e050,r8=pointer,r9=length,r11=packet,r12=available,r13=port*4)
        stop,r,writes=execute(code,memory,regs);copied=min(size-count,available);complete=count+copied==size
        expected=bytes([0xcc]*count)+bytes((i*17+3)&255 for i in range(copied))+bytes([0xcc]*(128-count-copied))
        if bytes(memory[dest+i] for i in range(128))!=expected:raise ValueError('Body copied bytes')
        if get(length)!=available-copied or get(0x2002e358+port*4)!=(0 if complete else count+copied):raise ValueError('Body counters')
        if get(pointer)!=(src+copied if complete else src):raise ValueError('Body pointer')
        if complete:
            if stop!=0x112fa or r['r4']!=(0 if flags else 1) or get(ctx+368)!=(3 if flags else 2):raise ValueError('Body completion')
        elif stop!=0x1140c:raise ValueError('Partial body boundary')
        cases+=1
    return {'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Stock copy starts after pointer/count validation and preparation. Partial path stops before async scheduling; no source-target comparison yet.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-body-copy-stock.json').write_text(json.dumps(r,indent=2)+'\n');print('Body copy cases:',r['decoded_cases'])
