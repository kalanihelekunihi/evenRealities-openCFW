# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
import verify_gx8002_dcache_clean_range as cache
from verify_gx8002_dma_transfer import verify as transfer_verify,execute,ROOT,decode


def verify():
    transfer=transfer_verify();dependency=cache.verify();old_cache,new_cache=cache.programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd104','--stop-address=0xd14c',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-dma-transfer/transfer.disassembly.txt').read_text());cases=calls=0
    for outer,leaf,channel,status in product((False,True),(False,True),(0,1),(0,1,0xffffffff)):
        seen=[]
        def hook(pointer,size):
            nonlocal calls
            actual=cache.execute(new_cache if leaf else old_cache,cache.ADDRESS if leaf else cache.OFFSET,pointer,size,0x12345678)
            if actual!=(cache.expected(pointer,size),True):raise ValueError('DMA cache trace')
            if len(actual[0])!=26:raise ValueError('DMA descriptor line count')
            seen.append(actual[0]);calls+=1
        result=execute(new if outer else old,0x10203b78 if outer else 0xd104,0x20060000,0xa0000000,80,channel,0x20040000,status,0xa1000000,cache_hook=hook)
        if len(seen)!=int(status!=0xffffffff):raise ValueError('DMA cache call condition')
        if result[0]!=(0xffffffff if status==0xffffffff else 0):raise ValueError('DMA cache return')
        cases+=1
    return {'transfer':transfer,'cache_dependency':dependency,'decoded_cases':cases,'cache_calls':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Separate decoded cache leaf frame; configuration remains modeled. Cache command writes do not prove hardware coherence.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-transfer-cache.json').write_text(json.dumps(result,indent=2)+'\n');print('Transfer cache cases:',result['decoded_cases'],result['cache_calls'])
