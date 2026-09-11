# SPDX-License-Identifier: MIT
"""Execute source-linked transmit setup with relocated helper targets."""
import json,struct
from itertools import product
from link_gx8002_dma_uart_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_transmit_dma import execute
from verify_gx8002_dma_callback import execute as register_callback
from verify_gx8002_dma_irq_handler import execute as interrupt
from verify_gx8002_uart_transmit_complete import execute as complete
from verify_gx8002_uart_flush import execute as flush


def verify(owned_storage=False):
    candidate=build(owned_dma=owned_storage,owned_irq=owned_storage,owned_uart=owned_storage);path=ROOT/'build/gx8002-dma-uart-source/dma-uart.elf'
    elf=Elf32(path.read_bytes(),str(path));sy={s['name']:s['value'] for s in elf.symbols() if s['name']}
    code=decode((path.parent/'dma-uart.disassembly.txt').read_text())
    names={'dcache_clean_range':0x10025664,'dma_select':0x10203a4c,'uart_dma_burst':0x10203050,'dma_callback':0x10203b64,'dma_transfer':0x10203b78,'dma_release':0x10203b38}
    registrations=0;dispatches=0;completions=0
    helpers={sy['open_cfw_gx8002_'+name]:address for name,address in names.items()};cases=0
    for port,channel,buffer,length in product((0,1) if owned_storage else (0,1,2,0xffffffff),(0,1,0xffffffff),(0,0x2005000f),(0,32,0xffffffff)):
        descriptor=0x20026a94;device=0xa0000000;initial=None
        if owned_storage:
            descriptor=sy['open_cfw_gx8002_uart_descriptors']+port*128
            section=next(s for s in elf.sections if s['name']=='.data')
            words=struct.unpack_from('<32I',elf.contents(section),descriptor-section['address'])
            initial={descriptor+i*4:value for i,value in enumerate(words)};device=words[1]
        callback_base=sy['open_cfw_gx8002_dma_callbacks'];callback_memory={callback_base+i*4:0 for i in range(4)}
        writes=[]
        def callback_hook(number,handler,private):
            nonlocal registrations
            actual=register_callback(code,sy['open_cfw_gx8002_dma_callback'],number,handler,private)
            expected=[(callback_base+number*4,handler),(callback_base+8+number*4,private)]
            if actual!=expected:raise ValueError('Relocated callback writes')
            for address,value in actual:
                if address not in callback_memory:raise ValueError('Callback outside owned table')
                callback_memory[address]=value
            writes.extend(actual);registrations+=1
        result,trace,memory=execute(code,sy['open_cfw_gx8002_uart_transmit_dma'],port,buffer,length,channel,3,4,0xffffffff,helper_addresses=helpers,descriptor_address=descriptor,initial_memory=initial,callback_hook=callback_hook)
        calls=[x for x in trace if x[0] not in ('read','write')]
        wanted=[('cache',buffer,length),('select',)]
        if channel!=0xffffffff:
            wanted += [('burst',descriptor,1),('burst',descriptor,1)]
            if port>1:wanted += [('release',channel)]
            else:wanted += [('callback',channel,sy['open_cfw_gx8002_uart_transmit_complete'],descriptor),('transfer',device,buffer,length,channel,(0,3,0,0,0,0,4,1,7 if port==0 else 5,1,0,1))]
        success=channel!=0xffffffff and port<2
        expected_callbacks={callback_base+i*4:0 for i in range(4)}
        if success:
            expected_callbacks[callback_base+channel*4]=sy['open_cfw_gx8002_uart_transmit_complete']
            expected_callbacks[callback_base+8+channel*4]=descriptor
        if callback_memory!=expected_callbacks or len(writes)!=(2 if success else 0):raise ValueError('Callback table state')
        if calls!=wanted or result!=(0 if success else 0xffffffff):raise ValueError('Relocated DMA call/result contract')
        if memory[descriptor+124]!=(channel if success else initial[descriptor+124] if initial is not None else 0xffffffff):raise ValueError('Relocated DMA channel state')
        if initial is not None:
            expected=dict(initial)
            if success:expected[descriptor+124]=channel
            if memory!=expected:raise ValueError('Owned UART unrelated state changed')
            if any(x[0] in ('read','write') and 0x20026a94<=x[1]<0x20026b94 for x in trace):raise ValueError('Stock descriptor access')
        if success:
            dispatched=[]
            def completion_hook(target,private):
                nonlocal completions
                dispatched.append((target,private))
                if not owned_storage:return
                # Application completion fields are inputs until buffer-entry composition.
                before=dict(memory);before[descriptor+108]=0x10380000;before[descriptor+112]=0x12345678
                helpers_complete={sy['open_cfw_gx8002_dma_release']:0x10203b38,sy['open_cfw_gx8002_uart_flush']:0x10203598}
                def drain(number):
                    return flush(code,sy['open_cfw_gx8002_uart_flush'],number,[0,32,64],descriptor_base=sy['open_cfw_gx8002_uart_descriptors'],device_base=device)
                completed_trace,after=complete(code,target,channel,port,0x10380000,0x12345678,False,
                    descriptor=private,initial_memory=before,helper_addresses=helpers_complete,flush_hook=drain)
                expected_after=dict(before);expected_after[descriptor+124]=0xffffffff
                if after!=expected_after:raise ValueError('Completion descriptor handoff')
                if completed_trace[-1]!=('callback',0x10380000,port,0x12345678):raise ValueError('Application completion arguments')
                events=[x[0] for x in completed_trace if x[0] in ('release','flush','callback')]
                if events!=['release','flush','callback']:raise ValueError('Relocated completion order')
                polls=[x for x in completed_trace if x[0]=='read' and x[1]==device+20]
                if polls!=[('read',device+20,x) for x in (0,32,64)]:raise ValueError('Completion decoded drain')
                completions+=1
            irq_helpers={sy['open_cfw_gx8002_dma_clear']:0x10203804,sy['open_cfw_gx8002_dma_deallocate']:0x10203a98}
            irq_result=interrupt(code,sy['open_cfw_gx8002_dma_irq_handler'],1<<channel,
                tuple(callback_memory[callback_base+i*4] for i in range(2)),False,0xffffffff,
                private_data=tuple(callback_memory[callback_base+8+i*4] for i in range(2)),
                state_address=sy['open_cfw_gx8002_dma_state'],callback_address=callback_base,
                helper_addresses=irq_helpers,callback_hook=completion_hook)
            if dispatched!=[(sy['open_cfw_gx8002_uart_transmit_complete'],descriptor)]:raise ValueError('Registered completion dispatch')
            events=[x[0] for x in irq_result[1] if x[0] in ('clear','deallocate','callback')]
            if events!=['clear','deallocate','callback']:raise ValueError('DMA dispatch ordering')
            dispatches+=1
        cases+=1
    return {'candidate':candidate,'owned_storage':owned_storage,'decoded_callback_calls':registrations,'decoded_irq_dispatches':dispatches,'decoded_completions':completions,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Actual relocated setup instructions; callback registration decoded into a modeled table; DMA ISR consumes registration output; owned-storage dispatch executes completion and drain; clear/deallocation/release effects modeled. Owned-storage mode loads actual compiled descriptor defaults; otherwise UART descriptors remain externally bound. Startup copying remains unqualified. Invalid-port repair checked against its explicit contract. Not a complete firmware image.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-transmit-dma-relocated.json').write_text(json.dumps(r,indent=2)+'\n');print('Relocated DMA cases:',r['decoded_cases'])
