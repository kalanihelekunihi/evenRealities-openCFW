# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from verify_gx8002_uart_transmit_dma import verify as setup_verify,execute as setup,ROOT,decode
from verify_gx8002_dma_transfer import verify as transfer_verify,execute as transfer
import verify_gx8002_dcache_clean_range as cache


def verify():
    candidate=setup_verify();dependency=transfer_verify();cache_dependency=cache.verify();old_cache,new_cache=cache.programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc694','--stop-address=0xd14c',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-uart-transmit-dma/dma.disassembly.txt').read_text())
    leaf_code=decode((ROOT/'build/gx8002-dma-transfer/transfer.disassembly.txt').read_text());cases=calls=cache_calls=0
    for outer,leaf,port,channel,length,status in product((False,True),(False,True),(0,1),(0,1,0xffffffff),(0,32,0xffffffff),(0,0xffffffff)):
        seen=[]
        def hook(dst,src,size,number,pointer,config):
            nonlocal calls
            if (dst,src,size,number,config)!=(0xa0000000,0x20050000,length,channel,(0,3,0,0,0,0,4,1,7 if port==0 else 5,1,0,1)):raise ValueError('Setup transfer configuration')
            cache_events=[]
            def cache_hook(address,count):
                nonlocal cache_calls
                if (address,count)!=(0x20050000,416):raise ValueError('Descriptor cache range')
                result=cache.execute(new_cache if leaf else old_cache,cache.ADDRESS if leaf else cache.OFFSET,address,count,0x12345678)
                if result!=(cache.expected(address,count),True):raise ValueError('Descriptor clean commands')
                cache_events.append(result[0]);cache_calls+=1
            actual=transfer(leaf_code if leaf else old,0x10203b78 if leaf else 0xd104,dst,src,size,number,pointer,status,0xa1000000,cache_hook=cache_hook)
            if len(cache_events)!=int(status!=0xffffffff):raise ValueError('Descriptor cache condition')
            wanted=[('configure',dst,src,size,number,pointer)]
            if status!=0xffffffff:wanted.append(('cache',0x20050000,416))
            if [x for x in actual[1] if x[0] in ('configure','cache')]!=wanted:raise ValueError('Nested transfer arguments')
            writes=[x for x in actual[1] if x[0]=='write' and x[1]>=0xa0000000]
            if writes!=([] if status==0xffffffff else [('write',0xa1000310,257<<number),('write',0xa10003a0,257<<number)]):raise ValueError('Nested transfer enable sequence')
            seen.append(actual);calls+=1;return actual[0]
        result=setup(new if outer else old,0x10203108 if outer else 0xc694,port,0x20050000,length,channel,3,4,0xffffffff,transfer_hook=hook)
        if result[0]!=(0xffffffff if channel==0xffffffff else 0) or len(seen)!=int(channel!=0xffffffff):raise ValueError('Setup ignored transfer error contract')
        cases+=1
    return {'candidate':candidate,'transfer_dependency':dependency,'cache_dependency':cache_dependency,'decoded_cache_calls':cache_calls,'decoded_cases':cases,'decoded_transfer_calls':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Decoded transfer wrapper; descriptor cache decoded; configure effects modeled. Setup config tuple and forwarded stack pointer checked separately. No physical DMA transfer or full firmware claim.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-transmit-dma-transfer.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'],r['decoded_transfer_calls'])
