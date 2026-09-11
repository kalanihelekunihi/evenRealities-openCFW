# SPDX-License-Identifier: MIT
"""Body calls composed with source/stock receive controls in isolated descriptors."""
import json,subprocess
from verify_gx8002_uart_receive_irq import verify as irq_verify
from verify_gx8002_uart_receive_control import execute,expected,decode,ROOT
from compare_gx8002_uart_body_full import verify as body_verify


def verify():
    dependency=irq_verify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xcc18','--stop-address=0xcc74',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new={kind:decode((ROOT/'build/gx8002-uart-receive-control'/(kind+'.disassembly.txt')).read_text()) for kind in ('start','stop')}
    counts={'start':0,'stop':0}
    def hook(kind,port,callback,private):
        offset=0xcc18 if kind=='start' else 0xcc4c
        for word,token in ((0,0),(1,0x40),(0xffffffff,0xffffffff)):
            wanted=expected(kind,port,callback,private,word,token)
            for source in (False,True):
                actual=execute(new[kind] if source else old,offset+0x101f6a74 if source else offset,kind,port,callback,private,word,token)
                if actual!=wanted:raise ValueError('Body receive control contract')
                counts[kind]+=1
        return wanted[0]
    body=body_verify(original_entry=True,control_hook=hook)
    return {'irq_dependency':dependency,'body':body,'control_executions':counts,'source_admitted':False,'hardware_qualified':False,'limits':['Receive controls execute in isolated descriptor/MMIO memory per call; cross-call and concurrent UART state are not yet composed. Async-buffer and queue boundaries remain modeled in this run. Control failure injection is overridden by actual decoded return values.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-body-control.json').write_text(json.dumps(result,indent=2)+'\n');print('Body control executions:',result['control_executions'])
