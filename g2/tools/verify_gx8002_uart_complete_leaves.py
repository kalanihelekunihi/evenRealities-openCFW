# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from verify_gx8002_uart_receive_complete import verify as complete_verify,execute as complete,ROOT,decode
from verify_gx8002_dma_release import verify as release_verify,execute as release
from verify_gx8002_dma_deallocate import execute as deallocate,expected
import verify_gx8002_dcache_clean_invalid_range as cache

def verify():
    completion=complete_verify();release_dependency=release_verify();cache_dependency=cache.verify();old_cache,new_cache=cache.programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc670','--stop-address=0xd0cc',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-uart-receive-complete/complete.disassembly.txt').read_text())
    new_release=decode((ROOT/'build/gx8002-dma-release/release.disassembly.txt').read_text())
    new_free=decode((ROOT/'build/gx8002-dma-deallocate/deallocate.disassembly.txt').read_text());cases=0
    for outer,leaf,channel,allocation,size in product((False,True),(False,True),(0,1),([1,1],[1,0],[0,1],[2,255]),(0,77,416,0xffffffff)):
        events=[]
        def release_hook(number):
            def deallocate_hook(value):return deallocate(new_free if leaf else old,0x10203a98 if leaf else 0xd024,allocation,0x80000040,value)
            result=release(new_release if leaf else old,0x10203b38 if leaf else 0xd0c4,number,deallocate_hook)
            if result!=expected(allocation,0x80000040,channel):raise ValueError('Completion release effects')
            events.append('release')
        def cache_hook(address,length):
            result=cache.execute(new_cache if leaf else old_cache,cache.ADDRESS if leaf else cache.OFFSET,address,length,0x12345678)
            if result!=(cache.expected(0x2005000f,size),True):raise ValueError('Completion cache effects')
            events.append('cache')
        result=complete(new if outer else old,0x102030e4 if outer else 0xc670,channel,1,0x2005000f,size,0x10207ee0,0x12345678,False,release_hook=release_hook,cache_hook=cache_hook)
        if events!=['release','cache'] or result[0][-1]!=('callback',0x10207ee0,1,0x12345678):raise ValueError('Completion order')
        if result[1][0x20026afc]!=0xffffffff:raise ValueError('Completion channel clear')
        cases+=1
    return {'completion':completion,'release_dependency':release_dependency,'cache_dependency':cache_dependency,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Separate descriptor, allocation and cache frames; callback delivery modeled. IRQ/clock internals remain modeled in deallocation. No physical DMA interrupt/coherence proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-complete-leaves.json').write_text(json.dumps(report,indent=2)+'\n');print('Completion leaf cases:',report['decoded_cases'])
