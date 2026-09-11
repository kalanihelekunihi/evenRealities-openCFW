# SPDX-License-Identifier: MIT
"""Qualify the explicit invalid-port repair, not stock-equivalent behavior."""
import json
from itertools import product
from verify_gx8002_uart_transmit_dma import execute,build,ROOT,decode
from verify_gx8002_dma_release import verify as verify_release,execute as release
from verify_gx8002_dma_deallocate import execute as deallocate,expected


def verify():
    candidate=build();dependency=verify_release()
    code=decode((ROOT/'build/gx8002-uart-transmit-dma/dma.disassembly.txt').read_text())
    release_code=decode((ROOT/'build/gx8002-dma-release/release.disassembly.txt').read_text())
    free_code=decode((ROOT/'build/gx8002-dma-deallocate/deallocate.disassembly.txt').read_text());cases=0
    for port,channel,allocation,token in product((2,3,0x80000000,0xffffffff),(0,1,0xffffffff),([1,1],[1,0],[0,1],[2,255]),(0,0x40,0xffffffff)):
        effects=[]
        def release_hook(number):
            result=release(release_code,0x10203b38,number,lambda c:deallocate(free_code,0x10203a98,allocation,token,c))
            if number!=channel or result!=expected(allocation,token,channel):raise ValueError('Cleanup allocation effects')
            effects.append(number)
        result,trace,memory=execute(code,0x10203108,port,0x20050000,32,channel,1,2,0xffffffff,release_hook=release_hook)
        calls=[x for x in trace if x[0] not in ('read','write')]
        wanted=[('cache',0x20050000,32),('select',)]
        if channel<0x80000000:wanted += [('burst',0x20026a94,1),('burst',0x20026a94,1),('release',channel)]
        if result!=0xffffffff or memory[0x20026b10]!=0xffffffff or calls!=wanted:raise ValueError('Invalid-port cleanup contract')
        if effects!=([] if channel>=0x80000000 else [channel]):raise ValueError('Cleanup release count')
        cases+=1
    return {'candidate':candidate,'release_dependency':dependency,'decoded_cases':cases,'stock_equivalent':False,'source_admitted':False,'hardware_qualified':False,'limits':['Explicit repair of stock uninitialized handshake use. Release/deallocation decoded in separate frames; IRQ and clock effects modeled. No hardware or firmware integration qualification.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-transmit-dma-cleanup.json').write_text(json.dumps(r,indent=2)+'\n');print('DMA cleanup cases:',r['decoded_cases'])
