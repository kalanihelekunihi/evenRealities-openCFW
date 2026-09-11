# SPDX-License-Identifier: MIT
"""Compose transmit DMA with decoded cache-range cleaning."""
import json,subprocess
from itertools import product
import verify_gx8002_dcache_clean_range as cache
from verify_gx8002_uart_transmit_dma import verify as dma_verify,execute,ROOT,decode

def verify():
    dma=dma_verify();dependency=cache.verify();old_cache,new_cache=cache.programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc694','--stop-address=0xc71c',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-uart-transmit-dma/dma.disassembly.txt').read_text());cases=calls=0
    for outer,leaf,port,channel,pointer,size in product((False,True),(False,True),(0,1),(0,0xffffffff),(0x20060000,0x2006000f,0xfffffff0),(0,1,77,128,129,416,0xffffffff)):
        seen=[]
        def hook(address,length):
            nonlocal calls
            if (address,length)!=(pointer,size):raise ValueError('Transmit transfer cache arguments')
            result=cache.execute(new_cache if leaf else old_cache,cache.ADDRESS if leaf else cache.OFFSET,address,length,0x12345678)
            if result!=(cache.expected(address,length),True):raise ValueError('Transmit cache commands')
            seen.append(result[0]);calls+=1
        result=execute(new if outer else old,0x10203108 if outer else 0xc694,port,pointer,size,channel,3,4,0xffffffff,cache_hook=hook,cache_buffer=0x20070000,cache_length=999)
        events=[x for x in result[1] if x[0] in ('cache','select')]
        if events!=[('cache',pointer,size),('select',)] or len(seen)!=1:raise ValueError('Transmit cache selection order')
        if result[0]!=(0xffffffff if channel==0xffffffff else 0):raise ValueError('Transmit cache return')
        cases+=1
    return {'dma_dependency':dma,'cache_dependency':dependency,'decoded_cases':cases,'decoded_cache_calls':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Separate decoded cache frame, including unused descriptor values differing from transfer arguments. DMA selection/burst/registration/transfer remain modeled here. Physical cache coherence unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-transmit-dma-cache.json').write_text(json.dumps(report,indent=2)+'\n');print('Transmit DMA cache cases:',report['decoded_cases'])
