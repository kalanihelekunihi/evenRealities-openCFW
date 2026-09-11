# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from analyze_gx8002_upstream_objects import ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from execute_gx8002_uart_prepare_stock import execute as stock
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_prepare import execute
from build_gx8002_uart_body_upstream_probe import build


def verify():
    probe=build();code=decode((ROOT/'build/gx8002-uart-body-probe/prepare-target.disassembly.txt').read_text());cases=0
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock preparation identity')
    original=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x11304','--stop-address=0x113b0',str(wrapper)],text=True))
    for index,flags,length,offset,capacity,pointer in product((0,7,15,16),(0,1),(0,3,4,20),(0,16,60),(4,32,64),(0,0x20050000)):
        base=0x2002e360;packet=0x20040000
        memory={base+i:0 for i in range(16*28)};memory.update({packet+i:0 for i in range(32)})
        def put(addr,value,size=4):
            for i in range(size):memory[addr+i]=(value>>(8*i))&255
        put(packet+4,0x101,2);put(packet+7,flags,1);put(packet+8,length,2);put(packet+16,0x1234);put(packet+24,99)
        if index<16:
            for off,value in ((4,0x101),(8,pointer),(12,capacity),(16,offset)):put(base+28*index+off,value)
        expected=memory.copy();body=(length-(4 if flags else 0))&0xffffffff
        def expected_put(addr,value):
            for i in range(4):expected[addr+i]=(value>>(8*i))&255
        valid=index<16 and body<=capacity
        start=0 if offset+length>capacity else offset
        if valid and start!=offset:expected_put(base+28*index+16,start)
        if valid and pointer:
            expected_put(packet+16,pointer+start);expected_put(base+28*index+16,start+body);result=0
        else:
            expected_put(packet+16,0);expected_put(packet+24,0);result=0xffffffff
        other=memory.copy()
        observed,source_writes=execute(code,memory)
        stock_result,stock_writes=stock(original,other)
        if stock_result!=result or other!=expected or stock_writes!=source_writes:raise ValueError(("stock",index,flags,length,offset,capacity,pointer))
        if observed!=result or memory!=expected:raise ValueError((index,flags,length,offset,capacity,pointer))
        cases+=1
    return {'probe':probe,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Stock inlined preparation and upstream target helper with finite registration states; boundaries modeled, full body reception pending.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-prepare-comparison.json').write_text(json.dumps(r,indent=2)+'\n');print('Preparation target cases:',r['decoded_cases'])
