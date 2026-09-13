# SPDX-License-Identifier: MIT
"""Helper mutation and rejected-port checks for the UART transmit callback."""
import json,subprocess
from itertools import product
from verify_gx8002_uart_send_callback import make_helper,oracle
from execute_gx8002_uart_send_callback import execute,word,BASE,MASK
from build_gx8002_uart_send_callback import ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11494','--stop-address=0x11624',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-uart-send-callback/callback.disassembly.txt').read_text());cases=0
    for port,state,budget,value,field in product((0,1),range(4),(0,1,4,14,32),(0,1,4,14,MASK),range(7)):
        ctx=BASE+380*port;memory={BASE+i:0 for i in range(1440)}
        word(memory,ctx+372,state);memory[ctx+67]=1;memory[ctx+68]=16;memory[ctx+80]=port
        memory[ctx+64]=0x34;memory[ctx+65]=0x12
        for i in range(6):
            row=0x2002e578+16*i;word(memory,row,port);word(memory,row+4,0x1234 if i==5 else i);word(memory,row+8,0x10310000+i*4);word(memory,row+12,i)
        target,address,size=(
          (0x10203604,0x2002e560+4*port,4),
          (0x10203604,0x2002e568+4*port,4),
          (0x102098a8,0x2002e568+4*port,4),
          (0x102077d4,ctx+64,2),
          (0x102077d4,ctx+80,1),
          (0x10207b38,ctx+67,1),
          (0x10310014,ctx+372,4))[field]
        def fresh():
            fired=[False]
            def mutate(t,m):
                if t==target and not fired[0]:
                    fired[0]=True
                    for i in range(size):m[address+i]=(value>>(8*i))&255
            return make_helper(1,0x87654321,mutate)
        expected=oracle(port,budget,memory,fresh())
        for code,entry in ((old,0x11494),(new,0x10207f08)):
            actual=execute(code,entry,port,budget,memory,fresh())
            if actual!=expected:raise ValueError(('Mutation',port,state,budget,value,field,hex(entry),actual[2],expected[2]))
        cases+=1
    rejected=0
    for port,length in product(tuple(range(2,256))+(0x102,0x80000002,MASK),(0,1,MASK)):
        expected=(('return',MASK),{},[('get',port&255)])
        for code,entry in ((old,0x11494),(new,0x10207f08)):
            if execute(code,entry,port,length,{},make_helper(1,0))!=expected:raise ValueError('Rejected port')
        rejected+=1
    return {'helper_mutation_cases':cases,'rejected_port_cases':rejected,'source_admitted':False,'limits':['One selected helper mutation per execution; finite memory effects, modeled helpers and valid full ports for array access. Rejected low-byte ports cover all remaining byte values and selected high-bit patterns.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-send-callback-mutations.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
