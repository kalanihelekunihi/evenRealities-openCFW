# SPDX-License-Identifier: MIT
"""Shutdown clearing executes the source-built memset body."""
import json,subprocess
from compare_gx8002_memset import verify as qualify,execute,expected
from verify_gx8002_uart_message_done import verify as shutdown
from build_gx8002_uart_message_done import ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    dependency=qualify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/memset-candidate.elf')],text=True));calls=0
    def hook(address,value,count,memory):
        nonlocal calls
        result=execute(code,0x102099cc,address,value,count)
        if result!=expected(address,value,count):raise ValueError('Nested fill trace')
        before=memory.copy()
        for a,size,v in result['trace']:
            for i in range(size):
                if a+i not in memory:raise ValueError('Nested fill bounds')
                memory[a+i]=(v>>(8*i))&255
        wanted=before.copy()
        for i in range(count):wanted[address+i]=value&255
        if memory!=wanted:raise ValueError('Nested fill memory')
        calls+=1;return result['result']
    comparison=shutdown(fill_hook=hook)
    return {'comparison':comparison,'fill_dependency':dependency,'fill_executions':calls,'source_admitted':False,'limits':['Decoded source memset writes caller memory at all shutdown clear boundaries; UART and selector modeled. Physical concurrency/hardware unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-message-done-fill.json').write_text(json.dumps(r,indent=2)+'\n');print(r['fill_executions'])
