# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from verify_gx8002_uart_dma_burst import verify as burst_verify,execute as burst_execute,ROOT,decode
from verify_gx8002_uart_transmit_dma import verify as dma_verify,execute as dma_execute


def verify():
    burst=burst_verify();dma=dma_verify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc5dc','--stop-address=0xc7a8',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new_burst=decode((ROOT/'build/gx8002-uart-dma-burst/burst.disassembly.txt').read_text())
    new_dma=decode((ROOT/'build/gx8002-uart-transmit-dma/dma.disassembly.txt').read_text());cases=0;calls=0
    mapping={1<<i:i-1 for i in range(2,11)}
    for outer_source,leaf_source,port,first,second in product((False,True),(False,True),(0,1),(0,4,64,1024,0xffffffff),(8,128,512)):
        def hook(descriptor,direction,index):
            nonlocal calls
            if descriptor!=0x20026a94 or direction!=1:raise ValueError('DMA burst arguments')
            tx=first if index==0 else second
            value,reads=burst_execute(new_burst if leaf_source else old,0x10203050 if leaf_source else 0xc5dc,tx,32,direction)
            if reads!=[(0x20026ac8,tx),(0x20026acc,32)]:raise ValueError('DMA burst reads')
            calls+=1;return value
        actual=dma_execute(new_dma if outer_source else old,0x10203108 if outer_source else 0xc694,port,0x20050000,80,3,0,0,0xffffffff,burst_hook=hook)
        transfers=[x for x in actual[1] if x[0]=='transfer']
        wanted=[('transfer',0xa0000000,0x20050000,80,3,(0,mapping.get(first,0),0,0,0,0,mapping.get(second,0),1,7 if port==0 else 5,1,0,1))]
        if transfers!=wanted or actual[0]!=0:raise ValueError('Transmit DMA burst composition')
        cases+=1
    return {'burst_dependency':burst,'dma_dependency':dma,'decoded_cases':cases,'burst_calls':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Separate descriptor snapshots at each leaf call, including changed transmit burst size between calls. Other DMA setup helpers remain modeled.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-transmit-dma-burst.json').write_text(json.dumps(result,indent=2)+'\n');print('DMA burst composition:',result['decoded_cases'],result['burst_calls'])
