# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from analyze_gx8002_upstream_objects import ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_body_validation_stock import execute as stock
from execute_gx8002_uart_body_validation_source import execute as source


def verify():
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x11348','--stop-address=0x113a6',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-body-probe/body.linked.disassembly.txt').read_text());cases=0
    for port,condition,status in product((0,1),('null_buffer','null_length_pointer','empty'),(0,0xffffffff)):
        ctx=0x20040000;pointer=0x20041000;length=pointer+4;memory={}
        def put(addr,value):
            for i in range(4):memory[addr+i]=(value>>(8*i))&255
        buffer=0 if condition=='null_buffer' else 0x20050000
        lengthptr=0 if condition=='null_length_pointer' else length
        put(ctx+8,port);put(pointer,buffer);put(length,0)
        other=memory.copy()
        _,sr,st=stock(old,memory,dict(r5=ctx,r8=pointer,r9=lengthptr),helper_result=status)
        _,nr,nt=source(new,other,dict(r3=buffer,r6=lengthptr,r10=ctx),helper_result=status)
        expected=[('restart',port,0x10208098,0)]
        if st!=expected or nt!=expected or sr['r4']!=0xffffffff or nr['r0']!=0xffffffff or memory!=other:raise ValueError('Body input validation mismatch')
        cases+=1
    return {'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Starts after initial buffer-pointer dereference; null pointer-to-pointer is not safe in the original source. Restart helper modeled; whole entry and callback execution pending.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-body-validation.json').write_text(json.dumps(r,indent=2)+'\n');print('Body validation cases:',r['decoded_cases'])
