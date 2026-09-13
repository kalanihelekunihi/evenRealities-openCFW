# SPDX-License-Identifier: MIT
"""Enqueue publication through decoded source queue-put."""
import json,subprocess
from itertools import product
from compare_gx8002_queue_put import verify_put
from compare_gx8002_queue_get import execute as queue_execute
from verify_gx8002_uart_message_enqueue import helper_for,oracle
from execute_gx8002_uart_message_enqueue import execute,word,BASE
from build_gx8002_uart_message_enqueue import ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    dependency=verify_put();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    queue=decode(subprocess.check_output([pre,'-dr','--section=.sram_text',str(ROOT/'build/gx8002-queue-put/queue-size.o')],text=True))
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x11948','--stop-address=0x119e4',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-uart-message-enqueue/callback.disassembly.txt').read_text());cases=0;calls=0
    for port,full,tail,sending,flags in product((0,1),(False,True),(0,32,224),(0,1),(0,1,255)):
        p=0x20040000;ctx=BASE+380*port;m={BASE+i:0 for i in range(760)};m.update({p+i:0 for i in range(32)})
        word(m,ctx+12,1);word(m,ctx+8,port);word(m,ctx+24,sending);word(m,p+16,0x20050000);word(m,p+24,17);m[p+20]=port;m[p+7]=flags
        def fresh():
            base=helper_for(0,1,0x12345678)
            def helper(t,args,memory,events):
                nonlocal calls
                value=base(t,args,memory,events)
                if t!=0x100261b8:return value
                packet=bytes(memory[args[1]+i] for i in range(32));q={0x2000+i:0xcc for i in range(256)};q.update({0x3000+i:v for i,v in enumerate(packet)})
                for off,v in enumerate((tail,(tail+(32 if full else 64))%256,0x2000,256,32)):word(q,0x1000+off*4,v)
                expected=q.copy()
                if not full:
                    for i,v in enumerate(packet):expected[0x2000+tail+i]=v
                    word(expected,0x1000,(tail+32)%256)
                value,_=queue_execute(queue,q,0)
                if value!=int(not full) or q!=expected:raise ValueError('Queue publication')
                calls+=1;return value
            return helper
        expected=oracle(m,p,fresh())
        for code,entry in ((old,0x11948),(new,0x102083bc)):
            a=execute(code,entry,p,0,m,fresh())
            if (a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])!=expected:raise ValueError('Enqueue queue composition')
        cases+=1
    return {'queue_dependency':dependency,'enqueue_cases':cases,'queue_executions':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Source queue executes in translated separate memory; full after initial modeled nonfull check included. Physical concurrency, shared queue/packet aliasing and actual cache effects unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-message-enqueue-queue.json').write_text(json.dumps(r,indent=2)+'\n');print(r['enqueue_cases'],r['queue_executions'])
