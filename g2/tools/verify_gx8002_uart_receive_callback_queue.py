# SPDX-License-Identifier: MIT
"""Execute source queue publication at whole receive-dispatcher boundaries."""
import json,subprocess
from itertools import product
from compare_gx8002_queue_put import verify_put
from compare_gx8002_queue_get import execute as queue_execute
from verify_gx8002_uart_receive_callback import helper_for
from gx8002_uart_receive_callback_oracle import oracle
from execute_gx8002_uart_receive_callback import execute,word,BASE
from build_gx8002_uart_receive_callback import ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    dependency=verify_put();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    queue=decode(subprocess.check_output([pre,'-dr','--section=.sram_text',str(ROOT/'build/gx8002-queue-put/queue-size.o')],text=True))
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x11624','--stop-address=0x11838',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-uart-receive-callback/callback.disassembly.txt').read_text());cases=0;calls=0
    for port,state,flags,full,tail in product((0,1),(1,2,3),(0,1,255),(False,True),(0,32,224)):
        ctx=BASE+380*port;memory={BASE+i:0 for i in range(1440)};memory.update({0x20026c74+i:0 for i in range(8)})
        word(memory,ctx+368,state);word(memory,0x20026c74+4*port,14)
        memory[ctx+35]=flags;memory[ctx+36]=0 if state==1 else 8
        data=bytes((0x12,0x34,0x56,0x78))
        def fresh():
            base=helper_for(data,1,True,0)
            def helper(target,args,m,events):
                nonlocal calls
                result=base(target,args,m,events)
                if target!=0x100261b8:return result
                packet=bytes(m[args[1]+i] for i in range(32))
                q={0x2000+i:0xcc for i in range(256)};q.update({0x3000+i:v for i,v in enumerate(packet)})
                head=(tail+32)%256 if full else (tail+64)%256
                for off,value in enumerate((tail,head,0x2000,256,32)):word(q,0x1000+off*4,value)
                expected=q.copy()
                if not full:
                    for i,value in enumerate(packet):expected[0x2000+tail+i]=value
                    word(expected,0x1000,(tail+32)%256)
                result,_=queue_execute(queue,q,0)
                if result!=int(not full) or q!=expected:raise ValueError('Nested queue result/memory')
                calls+=1
                return result
            return helper
        expected=oracle(port,len(data),memory,fresh())
        for code,entry in ((old,0x11624),(new,0x10208098)):
            a=execute(code,entry,port,len(data),memory,fresh())
            if (a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])!=expected:raise ValueError('Dispatcher queue composition')
        cases+=1
    return {'queue_dependency':dependency,'dispatcher_cases':cases,'queue_executions':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Decoded source queue in translated separate memory, full/available and tail wrap; stock/source dispatcher and oracle consume actual queue result. UART/CRC/body remain modeled. Shared-memory aliasing and physical concurrency unqualified.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-receive-callback-queue.json').write_text(json.dumps(result,indent=2)+'\n');print(result['dispatcher_cases'],result['queue_executions'])
