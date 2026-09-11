# SPDX-License-Identifier: MIT
"""Decoded IRQ -> release -> completion with persistent allocation state."""
import json,subprocess
from itertools import product
import verify_gx8002_dma_irq_handler as irq
import verify_gx8002_dma_deallocate as free
import verify_gx8002_dma_release as release
import verify_gx8002_uart_receive_complete as complete
import verify_gx8002_dma_clear as clear
import verify_gx8002_dcache_clean_invalid_range as cache
from verify_gx8002_memcpy_source import decode
ROOT=irq.ROOT

def verify():
    dependencies={'irq':irq.verify(),'release':release.verify(),'complete':complete.verify(),'clear':clear.verify(),'cache':cache.verify()}
    old_cache,new_cache=cache.programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc670','--stop-address=0xd0cc',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    names={'irq':('dma-irq-handler','irq_handler'),'free':('dma-deallocate','deallocate'),'release':('dma-release','release'),'complete':('uart-receive-complete','complete'),'clear':('dma-clear','clear')}
    source={k:decode((ROOT/f'build/gx8002-{folder}/{name}.disassembly.txt').read_text()) for k,(folder,name) in names.items()}
    cases=0;free_calls=0;completed=0
    for outer,leaves,pending,registered,initial,size in product((False,True),(False,True),(0,1,2,3,0xffffffff),range(4),product((0,1,2,255),repeat=2),(0,77,416,0xffffffff)):
        allocation=list(initial);events=[];descriptors={};expected_allocation=list(initial)
        def choose(name,stock,compiled):return (source[name],compiled) if leaves else (old,stock)
        def deallocate(channel):
            nonlocal free_calls
            wanted=free.expected(allocation,0x80000040,channel)
            result=free.execute(*choose('free',0xd024,0x10203a98),allocation,0x80000040,channel)
            if result!=wanted:raise ValueError('Persistent allocation transition')
            allocation[:]=[result[1][0x2002ecac+i] for i in range(2)]
            events.append(('free',channel,tuple(allocation),sum(x[0]=='resource' for x in result[0])))
            free_calls+=1
            return result
        def clear_hook(channel,device):
            trace=clear.execute(*choose('clear',0xcd90,0x10203804),channel,device)
            # Independently require the five interrupt-clear register stores.
            writes=[x for x in trace if x[0]=='write']
            if writes!=[('write',device+off,1<<channel) for off in (0x338,0x340,0x348,0x350,0x358)]:raise ValueError(('IRQ clear',trace))
            events.append(('clear',channel))
        def callback(target,private):
            nonlocal completed
            channel=(private-0x20026a94)//128
            if target!=0x102030e4 or channel not in (0,1):raise ValueError('IRQ completion binding')
            def release_hook(number):return release.execute(*choose('release',0xd0c4,0x10203b38),number,deallocate)
            def cache_hook(address,length):
                result=cache.execute(new_cache if leaves else old_cache,cache.ADDRESS if leaves else cache.OFFSET,address,length,0x12345678)
                if result!=(cache.expected(address,length),True):raise ValueError('Completion cache')
                events.append(('cache',channel,address,length))
            result=complete.execute(*choose('complete',0xc670,0x102030e4),channel,channel,0x2005000f+channel*0x1000,size,0x10207ee0,0x12345678,False,release_hook=release_hook,cache_hook=cache_hook,descriptor=private)
            if result[1][private+104]!=0xffffffff or result[0][-1]!=('callback',0x10207ee0,channel,0x12345678):raise ValueError('Completion descriptor/callback')
            descriptors[channel]=result[1];events.append(('delivered',channel));completed+=1
        result=irq.execute(source['irq'] if outer else old,0x10203adc if outer else 0xd068,pending,tuple(0x102030e4 if registered&(1<<i) else 0 for i in range(2)),False,0xffffffff,clear_hook,deallocate,callback,(0x20026a94,0x20026b14))
        wanted=[]
        for channel in range(2):
            if not pending&(1<<channel):continue
            wanted.append(('clear',channel));expected_allocation[channel]=0
            event=('free',channel,tuple(expected_allocation),int(1 not in expected_allocation));wanted.append(event)
            if registered&(1<<channel):
                wanted.extend([event,('cache',channel,0x2005000f+channel*0x1000,size),('delivered',channel)])
        if result[0]!=0 or events!=wanted or allocation!=expected_allocation:raise ValueError('IRQ completion independent sequence')
        cases+=1
    return {'dependencies':dependencies,'decoded_cases':cases,'deallocation_calls':free_calls,'completion_calls':completed,'source_admitted':False,'hardware_qualified':False,'limits':['Allocation bytes persist between IRQ deallocation and callback release, and across both channels. Decoded routines retain separate register/descriptor/MMIO frames. IRQ-mask and clock helper bodies, and final application callback remain modeled. Not a unified emulator or physical DMA/coherence proof.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-irq-completion.json').write_text(json.dumps(result,indent=2)+'\n');print({k:result[k] for k in ('decoded_cases','deallocation_calls','completion_calls')})
