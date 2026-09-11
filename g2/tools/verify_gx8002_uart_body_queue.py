# SPDX-License-Identifier: MIT
"""Whole-body call-boundary composition with the recovered queue implementation."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT
from verify_gx8002_memcpy_source import decode
from compare_gx8002_queue_put import verify_put
from compare_gx8002_queue_get import execute
from compare_gx8002_uart_body_full import verify as body


def verify():
    dependency=verify_put();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-dr','--section=.sram_text',str(ROOT/'build/gx8002-queue-put/queue-size.o')],text=True))
    calls=0
    def hook(packet):
        nonlocal calls
        # Run both queue states for each packet before returning the available-case result.
        for full in (False,True):
            memory={0x2000+i:0xcc for i in range(256)}
            memory.update({0x3000+i:b for i,b in enumerate(packet)})
            for offset,value in enumerate((224,0 if full else 64,0x2000,256,32)):
                for i in range(4):memory[0x1000+offset*4+i]=(value>>(8*i))&255
            expected=memory.copy()
            if not full:
                for i,b in enumerate(packet):expected[0x2000+224+i]=b
                for i in range(4):expected[0x1000+i]=0
            result,_=execute(code,memory,0)
            if result!=int(not full) or memory!=expected:raise ValueError('Body queue memory mismatch')
            calls+=1
        return 1
    comparison=body(original_entry=True,queue_hook=hook)
    return {'comparison':comparison,'queue_dependency':dependency,'queue_executions':calls,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Queue decoded in separate translated memory with full and available states. Outer run consumes available return; independent failure-return cases remain in baseline. UART helpers remain modeled.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-body-queue.json').write_text(json.dumps(r,indent=2)+'\n');print('Body queue executions:',r['queue_executions'])
