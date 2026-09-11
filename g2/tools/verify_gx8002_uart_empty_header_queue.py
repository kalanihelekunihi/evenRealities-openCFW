# SPDX-License-Identifier: MIT
"""Compose decoded empty-header publication with stock/upstream queue puts."""
import json,subprocess
from itertools import product
from verify_gx8002_uart_empty_header import execute,verify,ROOT,decode
from compare_gx8002_queue_put import verify_put
from compare_gx8002_queue_get import execute as queue


def verify_composed():
    outer_evidence=verify();dependency=verify_put()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    def dis(args):return decode(subprocess.check_output([pre,*args],text=True))
    outer=dis(['-D','--start-address=0x1180a','--stop-address=0x11828',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')])
    old=dis(['-D','--start-address=0x181cc','--stop-address=0x18226',str(ROOT/'build/gx8002-queue-put/stock.elf')])
    new=dis(['-dr','--section=.sram_text',str(ROOT/'build/gx8002-queue-put/queue-size.o')])
    cases=0
    for port,source,head,tail in product((0,1),(False,True),range(0,256,32),range(0,256,32)):
        calls=[]
        def hook(packet):
            memory={0x2000+i:0xcc for i in range(256)}
            memory.update({0x3000+i:b for i,b in enumerate(packet)})
            for index,value in enumerate((tail,head,0x2000,256,32)):
                for byte in range(4):memory[0x1000+index*4+byte]=(value>>(byte*8))&255
            expected=memory.copy();full=(tail+32)%256==head
            if not full:
                for i,b in enumerate(packet):expected[0x2000+tail+i]=b
                for i in range(4):expected[0x1000+i]=(((tail+32)%256)>>(i*8))&255
            result,trace=queue(new if source else old,memory,0 if source else 0x181cc)
            if result!=int(not full) or memory!=expected:raise ValueError('Queue publication mismatch')
            calls.append(result);return result
        trace,state,magic,length=execute(outer,port,0,queue_hook=hook)
        if (state,magic,length)!=(0,0,0) or len(calls)!=1:raise ValueError('Empty header cleanup mismatch')
        cases+=1
    return {'decoded_cases':cases,'outer':outer_evidence,'queue_dependency':dependency,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Separate decoded frames and translated queue/packet addresses; 32-byte records in eight slots, all aligned head/tail states. No concurrent mutation or full callback qualification.']}

if __name__=='__main__':
    report=verify_composed();(ROOT/'docs/research/gx8002-uart-empty-header-queue.json').write_text(json.dumps(report,indent=2)+'\n');print('Empty header queue cases:',report['decoded_cases'])
