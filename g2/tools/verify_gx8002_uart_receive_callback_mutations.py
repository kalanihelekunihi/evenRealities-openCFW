# SPDX-License-Identifier: MIT
"""Receive dispatcher helper mutations and rejected ports."""
import json,subprocess
from itertools import product
from verify_gx8002_uart_receive_callback import helper_for
from gx8002_uart_receive_callback_oracle import oracle
from execute_gx8002_uart_receive_callback import execute,word,BASE,MASK
from build_gx8002_uart_receive_callback import ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11624','--stop-address=0x11838',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-uart-receive-callback/callback.disassembly.txt').read_text());cases=0
    for port,state,length,value,field in product((0,1),range(4),(1,4,10,16),(0,1,3,MASK),range(8)):
        ctx=BASE+380*port;memory={BASE+i:0 for i in range(1440)};memory.update({0x20026c74+i:0 for i in range(8)})
        word(memory,ctx+368,state);word(memory,0x20026c74+4*port,14);word(memory,ctx,0x12345678);word(memory,ctx+28,0x12345678)
        memory[ctx+35]=1;memory[ctx+36]=8
        target,address,size=(
          (0x102035d8,ctx+368,4),(0x102098a8,ctx+36,2),
          (0x102098a8,ctx+35,1),(0x10207cec,ctx+36,2),
          (0x10207cec,ctx+35,1),(0x100261b8,ctx+28,4),
          (0x100261b8,ctx+52,4),(0x100261b8,ctx+368,4))[field]
        data=bytes((i*17)&255 for i in range(length))
        def fresh():
            base=helper_for(data,1,True,MASK);fired=[False]
            def helper(t,args,m,events):
                result=base(t,args,m,events)
                if t==target and not fired[0]:
                    fired[0]=True
                    for i in range(size):m[address+i]=(value>>(8*i))&255
                return result
            return helper
        expected=oracle(port,length,memory,fresh())
        for code,entry in ((old,0x11624),(new,0x10208098)):
            a=execute(code,entry,port,length,memory,fresh());actual=(a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])
            if actual!=expected:raise ValueError(('Mutation',port,state,length,value,field,hex(entry),actual[2],expected[2],[(hex(k),actual[1].get(k),expected[1].get(k)) for k in set(actual[1])|set(expected[1]) if actual[1].get(k)!=expected[1].get(k)][:10]))
        cases+=1
    rejected=0
    for port,length in product(tuple(range(2,256))+(0x102,0x80000002,MASK),(0,1,MASK)):
        expected=(('return',MASK),{},[('get',port&255)])
        for code,entry in ((old,0x11624),(new,0x10208098)):
            a=execute(code,entry,port,length,{},helper_for(b'',0,False,0))
            if (a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])!=expected:raise ValueError('Rejected port')
        rejected+=1
    return {'helper_mutation_cases':cases,'rejected_port_cases':rejected,'source_admitted':False,'limits':['Single selected helper mutation, independent oracle and stock/source execution. Physical UART, concurrency and arbitrary aliasing remain unqualified.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-receive-callback-mutations.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
