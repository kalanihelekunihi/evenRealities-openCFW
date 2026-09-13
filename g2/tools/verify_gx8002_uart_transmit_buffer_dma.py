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
from verify_gx8002_uart_dma_burst import execute as burst
from verify_gx8002_dcache_clean_range import execute as clean,expected as expected_clean
from verify_gx8002_dma_select import execute as select,expected as expected_select
from verify_gx8002_uart_receive_irq import irq_execute
from verify_gx8002_dma_uart_clock_link import execute as gate,oracle as gate_oracle
from verify_gx8002_dma_clear import execute as clear
from verify_gx8002_dma_deallocate import execute as deallocate,expected as expected_deallocate
from verify_gx8002_dma_release import execute as release
from execute_gx8002_linked_uart_transfer import execute as transfer_execute


def verify():
    candidate=build(owned_dma=True,owned_irq=True,owned_uart=True)
    path=ROOT/'build/gx8002-dma-uart-source/dma-uart.elf';elf=Elf32(path.read_bytes(),str(path))
    sy={s['name']:s['value'] for s in elf.symbols() if s['name']};code=decode((path.parent/'dma-uart.disassembly.txt').read_text())
    section=next(s for s in elf.sections if s['name']=='.data');data=elf.contents(section);table=sy['open_cfw_gx8002_uart_descriptors']
    clock_base=sy['gx_clock_param_table'];clock_table=data[clock_base-section['address']:clock_base-section['address']+416]
    ro=next(s for s in elf.sections if s['name']=='.rodata');jumps=elf.contents(ro)
    names={'dcache_clean_range':0x10025664,'dma_select':0x10203a4c,'uart_dma_burst':0x10203050,'dma_callback':0x10203b64,'dma_transfer':0x10203b78,'dma_release':0x10203b38}
    dma_helpers={sy['open_cfw_gx8002_'+n]:v for n,v in names.items()}
    outer_helpers={sy['open_cfw_gx8002_uart_transmit_dma']:0x10203108,sy['open_cfw_gx8002_irq_save']:0x10025560,sy['open_cfw_gx8002_irq_restore']:0x1002556c};cases=calls=completions=burst_calls=cache_calls=selection_calls=gate_calls=0
    clear_calls=deallocation_calls=release_calls=disable_calls=0
    transfer_counts={key:0 for key in ('transfers','configurations','descriptors','clears','caches','translations')}
    for port,buffer,callback,length,channel in product((0,1),(0,0x20050000),(0,0x10380000),(0,32,0xffffffff),(0,1,0xffffffff)):
        d=table+port*128;words=struct.unpack_from('<32I',data,d-section['address']);device=words[1]
        initial={d+i*4:v for i,v in enumerate(words)};initial[d+44]=1;initial[device+0xa8]=0;initial[device+4]=0
        seen=[];cb_base=sy['open_cfw_gx8002_dma_callbacks'];cb_memory={cb_base+i*4:0 for i in range(4)}
        allocation=[0,0] if channel==0 else [1,0] if channel==1 else [1,1]
        state=sy['open_cfw_gx8002_dma_state']
        def registration(number,handler,private):
            writes=register(code,sy['open_cfw_gx8002_dma_callback'],number,handler,private)
            if writes!=[(cb_base+number*4,handler),(cb_base+8+number*4,private)]:raise ValueError('Buffer callback table')
            cb_memory.update(writes)
        def setup(pointer,address,count,memory):
            nonlocal calls
            if (pointer,address,count)!=(d,buffer,length):raise ValueError('Buffer setup handoff')
            def select_hook():
                nonlocal selection_calls
                state=sy['open_cfw_gx8002_dma_state']
                helpers={sy['open_cfw_gx8002_irq_save']:0x10025560,sy['open_cfw_gx8002_irq_restore']:0x1002556c,sy['open_cfw_gx8002_platform_gate']:0x10025080}
                psr=[0x40];transitions=[]
                def irq_hook(save,argument):
                    value,psr[0]=irq_execute(code,sy['open_cfw_gx8002_irq_save' if save else 'open_cfw_gx8002_irq_restore'],psr[0],argument)
                    transitions.append(psr[0]);return value
                def gate_hook(module,enabled):
                    nonlocal gate_calls
                    if (module,enabled)!=(25,1) or psr[0]!=0:raise ValueError('Selection gate IRQ exclusion')
                    actual=gate(code,sy['open_cfw_gx8002_platform_gate'],jumps,clock_table,module,enabled,0xa5a5a5a5,0,clock_base,ro['address'],sy['__module_get_info'])
                    if actual!=gate_oracle(clock_table,module,enabled,0xa5a5a5a5):raise ValueError('Submission decoded gate effects')
                    gate_calls+=1
                actual=select(code,sy['open_cfw_gx8002_dma_select'],allocation,0x40,state_address=state,helper_addresses=helpers,irq_hook=irq_hook,gate_hook=gate_hook)
                if transitions!=[0,0x40]:raise ValueError('Submission IRQ restoration')
                wanted=expected_select(allocation,0x40)
                def address(value):return value-0x2002e93c+state
                wanted_trace=[(x[0],address(x[1]),x[2]) if x[0] in ('read','write') else x for x in wanted[1]]
                wanted_memory={address(k):v for k,v in wanted[2].items()}
                if actual!=(channel,wanted_trace,wanted_memory):raise ValueError('Submission decoded allocation')
                allocation[:]=[actual[2][state+0x370+i] for i in range(2)]
                selection_calls+=1;return actual[0]
            cache_events=[]
            def cache_hook(start,size):
                nonlocal cache_calls
                if (start,size)!=(address,count):raise ValueError('Submission cache range')
                actual=clean(code,sy['open_cfw_gx8002_dcache_clean_range'],start,size,0x12345678)
                if actual!=(expected_clean(start,size),True):raise ValueError('Submission cache commands')
                cache_events.append(actual[0]);cache_calls+=1
            def burst_hook(desc,direction,index):
                nonlocal burst_calls
                if (desc,direction)!=(d,1):raise ValueError('Buffer burst arguments')
                value,reads=burst(code,sy['open_cfw_gx8002_uart_dma_burst'],memory[d+52],memory[d+56],direction,descriptor_address=desc)
                wanted={1<<i:i-1 for i in range(2,11)}.get(memory[d+52],0)
                if value!=wanted or reads!=[(d+52,memory[d+52]),(d+56,memory[d+56])]:raise ValueError('Buffer decoded burst contract')
                burst_calls+=1;return value
            def transfer_hook(dst,src,size,number,config,fields):
                expected_burst={1<<i:i-1 for i in range(2,11)}.get(memory[d+52],0)
                wanted=(0,expected_burst,0,0,0,0,expected_burst,1,7 if port==0 else 5,1,0,1)
                if fields!=wanted or (dst,src,size,number)!=(device,address,count,channel):raise ValueError('Linked UART transfer configuration')
                status,counts=transfer_execute(code,sy,dst,src,size,number,config,fields)
                for key,value in counts.items():transfer_counts[key]+=value
                return status
            result,trace,after=dma_execute(code,sy['open_cfw_gx8002_uart_transmit_dma'],port,address,count,channel,3,4,0xffffffff,descriptor_address=pointer,initial_memory=memory,helper_addresses=dma_helpers,callback_hook=registration,burst_hook=burst_hook,cache_hook=cache_hook,select_hook=select_hook,transfer_hook=transfer_hook)
            if len(cache_events)!=1:raise ValueError('Submission cache call count')
            seen.append(trace);calls+=1;return result,after
        result,trace,memory=buffer_execute(code,sy['open_cfw_gx8002_uart_transmit_buffer'],port,buffer,length,callback,0x12345678,0,0x40,1,0,descriptor_base=table,initial_memory=initial,helper_addresses=outer_helpers,dma_hook=setup)
        valid=bool(buffer and callback);success=valid and channel!=0xffffffff
        expected=dict(initial);expected[0x2002f000]=0x12345678
        if valid:expected.update({d+108:callback,d+68:2,d+116:buffer,d+120:length,d+112:0x12345678,d+124:channel if success else 0xffffffff,device+0xa8:1})
        if memory!=expected or result!=(0 if success else 0xffffffff) or len(seen)!=int(valid):raise ValueError('Buffer/DMA state and result')
        if success:
            delivered=[]
            def clear_status(number,base):
                nonlocal clear_calls
                actual=clear(code,sy['open_cfw_gx8002_dma_clear'],number,base,state_address=state)
                wanted=[('read',state,base)]+[('write',(base+off)&0xffffffff,1<<number) for off in (0x338,0x340,0x348,0x350,0x358)]
                if actual!=wanted:raise ValueError('Completion decoded status clearing')
                clear_calls+=1
            def free_channel(number):
                nonlocal deallocation_calls
                psr=[0x40];transitions=[]
                def irq_hook(save,argument):
                    value,psr[0]=irq_execute(code,sy['open_cfw_gx8002_irq_save' if save else 'open_cfw_gx8002_irq_restore'],psr[0],argument)
                    transitions.append(psr[0]);return value
                def gate_hook(module,enabled):
                    nonlocal disable_calls
                    if (module,enabled)!=(25,0) or psr[0]!=0:raise ValueError('Deallocation gate IRQ exclusion')
                    actual=gate(code,sy['open_cfw_gx8002_platform_gate'],jumps,clock_table,module,enabled,0xa5a5a5a5,0,clock_base,ro['address'],sy['__module_get_info'])
                    if actual!=gate_oracle(clock_table,module,enabled,0xa5a5a5a5):raise ValueError('Completion decoded gate effects')
                    disable_calls+=1
                helpers={sy['open_cfw_gx8002_irq_save']:0x10025560,sy['open_cfw_gx8002_irq_restore']:0x1002556c,sy['open_cfw_gx8002_platform_gate']:0x10025080}
                actual=deallocate(code,sy['open_cfw_gx8002_dma_deallocate'],allocation,0x40,number,gate_hook=gate_hook,irq_hook=irq_hook,state_address=state,helper_addresses=helpers)
                wanted_trace,wanted_memory=expected_deallocate(allocation,0x40,number)
                def relocated(value):return value-0x2002e93c+state
                wanted_trace=[(x[0],relocated(x[1]),x[2]) if x[0] in ('read','write') else x for x in wanted_trace]
                wanted_memory={relocated(k):v for k,v in wanted_memory.items()}
                if actual!=(wanted_trace,wanted_memory) or transitions!=[0,0x40]:raise ValueError('Completion decoded deallocation')
                allocation[:]=[actual[1][state+0x370+i] for i in range(2)]
                deallocation_calls+=1
            def release_channel(number):
                nonlocal release_calls
                release(code,sy['open_cfw_gx8002_dma_release'],number,free_channel,deallocate_address=sy['open_cfw_gx8002_dma_deallocate'])
                release_calls+=1
            def completion(target,private):
                nonlocal completions
                if (target,private)!=(sy['open_cfw_gx8002_uart_transmit_complete'],d):raise ValueError('Buffer completion dispatch')
                helpers={sy['open_cfw_gx8002_dma_release']:0x10203b38,sy['open_cfw_gx8002_uart_flush']:0x10203598}
                def drain(number):
                    return flush(code,sy['open_cfw_gx8002_uart_flush'],number,[0,64],descriptor_base=table,device_base=device)
                events,after=complete(code,target,channel,port,callback,0x12345678,False,descriptor=private,initial_memory=memory,helper_addresses=helpers,flush_hook=drain,release_hook=release_channel)
                expected_after=dict(memory);expected_after[d+124]=0xffffffff
                if after!=expected_after:raise ValueError('Buffer completion state')
                delivered.extend(x for x in events if x[0]=='callback');completions+=1
            helpers={sy['open_cfw_gx8002_dma_clear']:0x10203804,sy['open_cfw_gx8002_dma_deallocate']:0x10203a98}
            interrupt(code,sy['open_cfw_gx8002_dma_irq_handler'],1<<channel,
                tuple(cb_memory[cb_base+i*4] for i in range(2)),False,0xffffffff,
                private_data=tuple(cb_memory[cb_base+8+i*4] for i in range(2)),
                state_address=sy['open_cfw_gx8002_dma_state'],callback_address=cb_base,
                helper_addresses=helpers,callback_hook=completion,clear_hook=clear_status,deallocate_hook=free_channel)
            if delivered!=[('callback',callback,port,0x12345678)]:raise ValueError('Application buffer completion')
            if allocation!=([0,0] if channel==0 else [1,0]):raise ValueError('Completion allocation lifecycle')
        elif any(cb_memory.values()):raise ValueError('Registration on failed buffer submission')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'decoded_setup_calls':calls,'decoded_completions':completions,'decoded_burst_calls':burst_calls,'decoded_cache_calls':cache_calls,'decoded_selection_calls':selection_calls,'decoded_gate_calls':gate_calls,'decoded_clear_calls':clear_calls,'decoded_deallocation_calls':deallocation_calls,'decoded_release_calls':release_calls,'decoded_disable_calls':disable_calls,'decoded_transfer':transfer_counts,'source_admitted':False,'hardware_qualified':False,'limits':['Source defaults and application parameters feed decoded buffer/setup frames. DMA mode and interrupt arrival are modeled. Transfer, configuration, bus translation, descriptor generation and descriptor cache publication execute linked source code in separate frames with explicit handoffs. Allocation persists from selection through ISR and completion; IRQ and clock leaves are decoded. Descriptor memory is isolated; startup and physical execution unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-transmit-buffer-dma.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'],r['decoded_setup_calls'])
