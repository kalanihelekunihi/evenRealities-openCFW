# SPDX-License-Identifier: MIT
import json,struct
from itertools import product
from link_gx8002_dma_uart_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_transmit_buffer import execute as buffer_execute
from verify_gx8002_uart_transmit_dma import execute as dma_execute
from verify_gx8002_dma_callback import execute as register
from verify_gx8002_dma_irq_handler import execute as interrupt
from verify_gx8002_uart_transmit_complete import execute as complete
from verify_gx8002_uart_flush import execute as flush


def verify():
    candidate=build(owned_dma=True,owned_irq=True,owned_uart=True)
    path=ROOT/'build/gx8002-dma-uart-source/dma-uart.elf';elf=Elf32(path.read_bytes(),str(path))
    sy={s['name']:s['value'] for s in elf.symbols() if s['name']};code=decode((path.parent/'dma-uart.disassembly.txt').read_text())
    section=next(s for s in elf.sections if s['name']=='.data');data=elf.contents(section);table=sy['open_cfw_gx8002_uart_descriptors']
    names={'dcache_clean_range':0x10025664,'dma_select':0x10203a4c,'uart_dma_burst':0x10203050,'dma_callback':0x10203b64,'dma_transfer':0x10203b78,'dma_release':0x10203b38}
    dma_helpers={sy['open_cfw_gx8002_'+n]:v for n,v in names.items()}
    outer_helpers={sy['open_cfw_gx8002_uart_transmit_dma']:0x10203108,sy['open_cfw_gx8002_irq_save']:0x10025560,sy['open_cfw_gx8002_irq_restore']:0x1002556c};cases=calls=completions=0
    for port,buffer,callback,length,channel in product((0,1),(0,0x20050000),(0,0x10380000),(0,32,0xffffffff),(0,1,0xffffffff)):
        d=table+port*128;words=struct.unpack_from('<32I',data,d-section['address']);device=words[1]
        initial={d+i*4:v for i,v in enumerate(words)};initial[d+44]=1;initial[device+0xa8]=0;initial[device+4]=0
        seen=[];cb_base=sy['open_cfw_gx8002_dma_callbacks'];cb_memory={cb_base+i*4:0 for i in range(4)}
        def registration(number,handler,private):
            writes=register(code,sy['open_cfw_gx8002_dma_callback'],number,handler,private)
            if writes!=[(cb_base+number*4,handler),(cb_base+8+number*4,private)]:raise ValueError('Buffer callback table')
            cb_memory.update(writes)
        def setup(pointer,address,count,memory):
            nonlocal calls
            if (pointer,address,count)!=(d,buffer,length):raise ValueError('Buffer setup handoff')
            result,trace,after=dma_execute(code,sy['open_cfw_gx8002_uart_transmit_dma'],port,address,count,channel,3,4,0xffffffff,descriptor_address=pointer,initial_memory=memory,helper_addresses=dma_helpers,callback_hook=registration)
            seen.append(trace);calls+=1;return result,after
        result,trace,memory=buffer_execute(code,sy['open_cfw_gx8002_uart_transmit_buffer'],port,buffer,length,callback,0x12345678,0,0x40,1,0,descriptor_base=table,initial_memory=initial,helper_addresses=outer_helpers,dma_hook=setup)
        valid=bool(buffer and callback);success=valid and channel!=0xffffffff
        expected=dict(initial);expected[0x2002f000]=0x12345678
        if valid:expected.update({d+108:callback,d+68:2,d+116:buffer,d+120:length,d+112:0x12345678,d+124:channel if success else 0xffffffff,device+0xa8:1})
        if memory!=expected or result!=(0 if success else 0xffffffff) or len(seen)!=int(valid):raise ValueError('Buffer/DMA state and result')
        if success:
            delivered=[]
            def completion(target,private):
                nonlocal completions
                if (target,private)!=(sy['open_cfw_gx8002_uart_transmit_complete'],d):raise ValueError('Buffer completion dispatch')
                helpers={sy['open_cfw_gx8002_dma_release']:0x10203b38,sy['open_cfw_gx8002_uart_flush']:0x10203598}
                def drain(number):
                    return flush(code,sy['open_cfw_gx8002_uart_flush'],number,[0,64],descriptor_base=table,device_base=device)
                events,after=complete(code,target,channel,port,callback,0x12345678,False,descriptor=private,initial_memory=memory,helper_addresses=helpers,flush_hook=drain)
                expected_after=dict(memory);expected_after[d+124]=0xffffffff
                if after!=expected_after:raise ValueError('Buffer completion state')
                delivered.extend(x for x in events if x[0]=='callback');completions+=1
            helpers={sy['open_cfw_gx8002_dma_clear']:0x10203804,sy['open_cfw_gx8002_dma_deallocate']:0x10203a98}
            interrupt(code,sy['open_cfw_gx8002_dma_irq_handler'],1<<channel,
                tuple(cb_memory[cb_base+i*4] for i in range(2)),False,0xffffffff,
                private_data=tuple(cb_memory[cb_base+8+i*4] for i in range(2)),
                state_address=sy['open_cfw_gx8002_dma_state'],callback_address=cb_base,
                helper_addresses=helpers,callback_hook=completion)
            if delivered!=[('callback',callback,port,0x12345678)]:raise ValueError('Application buffer completion')
        elif any(cb_memory.values()):raise ValueError('Registration on failed buffer submission')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'decoded_setup_calls':calls,'decoded_completions':completions,'source_admitted':False,'hardware_qualified':False,'limits':['Source defaults and application parameters feed decoded buffer/setup frames. DMA mode is modeled as already configured; registration, ISR, completion and drain decoded; other setup/ISR/release effects modeled. Startup and physical execution unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-transmit-buffer-dma.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'],r['decoded_setup_calls'])
