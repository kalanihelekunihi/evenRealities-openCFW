# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from verify_gx8002_uart_receive_dma import verify as dma_verify,execute as dma_execute,ROOT,decode
from verify_gx8002_dma_callback import verify as callback_verify,execute as callback_execute

def verify():
    dma=dma_verify();callback=callback_verify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc71c','--stop-address=0xd104',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-uart-receive-dma/dma.disassembly.txt').read_text());new_callback=decode((ROOT/'build/gx8002-dma-callback/callback.disassembly.txt').read_text());cases=calls=0
    for outer,leaf,port,channel,status in product((False,True),(False,True),(0,1,2),(0,1,0xffffffff),(0,0xffffffff)):
        seen=[]
        def hook(number,handler,private):
            nonlocal calls
            if (number,handler,private)!=(channel,0x102030e4,0x20026a94):raise ValueError('Receive callback arguments')
            writes=callback_execute(new_callback if leaf else old,0x10203b64 if leaf else 0xd0f0,number,handler,private)
            wanted=[(0x20027320+channel*4,handler),(0x20027328+channel*4,private)]
            if writes!=wanted:raise ValueError('Receive callback storage')
            seen.append(writes);calls+=1
        result=dma_execute(new if outer else old,0x10203190 if outer else 0xc71c,port,0x20050000,80,channel,3,4,status,callback_hook=hook)
        successful=channel!=0xffffffff and port<2
        if len(seen)!=int(successful) or result[0]!=(0 if successful else 0xffffffff):raise ValueError('Receive registration condition')
        events=[x[0] for x in result[1] if x[0] in ('callback','transfer')]
        if events!=(['callback','transfer'] if successful else []):raise ValueError('Receive registration order')
        cases+=1
    return {'dma_dependency':dma,'callback_dependency':callback,'decoded_cases':cases,'decoded_callback_calls':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Registration leaf writes compared in isolation; callback invocation and transfer remain separate dependencies. Other receive-DMA helpers modeled.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-receive-dma-callback.json').write_text(json.dumps(report,indent=2)+'\n');print('Receive callback cases:',report['decoded_cases'],report['decoded_callback_calls'])
