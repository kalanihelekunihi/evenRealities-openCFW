# SPDX-License-Identifier: MIT
import json,struct
from itertools import product
from link_gx8002_uart_configure_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_configure import arithmetic
from execute_gx8002_uart_configure import execute
from verify_gx8002_uart_fifo_depth import execute as fifo
from execute_gx8002_linked_irq_registration import execute as irq
from compare_gx8002_irq_dispatch import execute as dispatch
from execute_gx8002_uart_interrupt import execute as interrupt


def verify(initialize=False,decoded_frequency=False):
    if decoded_frequency and not initialize:raise ValueError("Frequency composition requires initialization")
    candidate=build(include_initialize=initialize);path=ROOT/('build/gx8002-uart-initialize-source/uart.elf' if initialize else 'build/gx8002-uart-configure-source/uart.elf');elf=Elf32(path.read_bytes(),str(path))
    sy={s['name']:s['value'] for s in elf.symbols() if s['name']};code=decode((path.parent/'uart.disassembly.txt').read_text())
    section=next(s for s in elf.sections if s['name']=='.data');data=elf.contents(section)
    control_calls=0
    frequency_calls=0
    def frequency_hook(module):
        nonlocal frequency_calls
        if module!=16:raise ValueError('UART frequency module')
        from verify_gx8002_uart_frequency_relocated import verify as frequency
        result=frequency(elf,code,clock);frequency_calls+=1
        return result['result_hz']
    gate_calls=0
    if initialize:
        from verify_gx8002_dma_uart_clock_link import execute as gate_execute
        from compare_gx8002_platform_gate import oracle as gate_oracle
        all_symbols=list(elf.symbols());gate_symbol=next(x for x in all_symbols if x['name']=='open_cfw_gx8002_platform_gate')
        targets={int(args,0) for pc,(op,args,width) in code.items() if gate_symbol['value']<=pc<gate_symbol['value']+gate_symbol['size'] and op=='bsr'}
        if len(targets)!=1:raise ValueError('Gate lookup target')
        lookup=targets.pop();lookup_symbol=next(x for x in all_symbols if x['value']==lookup and x['size'])
        literals={int(args.split(',')[1],0) for pc,(op,args,width) in code.items() if lookup<=pc<lookup+lookup_symbol['size'] and op=='lrw'}
        tables=[x for x in all_symbols if x['name']=='gx_clock_param_table' and x['value'] in literals]
        if len(tables)!=1:raise ValueError('Gate table resolution')
        table_base=tables[0]['value'];table_data=data[table_base-section['address']:table_base-section['address']+416]
        ro=next(x for x in elf.sections if x['name']=='.rodata')
        def gate_hook(module,enabled):
            nonlocal gate_calls
            result=gate_execute(code,gate_symbol['value'],elf.contents(ro),table_data,module,enabled,0xa5a5a5a5,0,table_base,ro['address'],lookup)
            if result!=gate_oracle(table_data,module,enabled,0xa5a5a5a5):raise ValueError('Initializer decoded gate')
            gate_calls+=1
    names=dict(uint='__floatunsidf',divide='__divdf3',multiply='__muldf3',add='__adddf3',fix='__fixunsdfsi',pack='__pack_d',unpack='__unpack_d',core='_fpadd_parts',compare='__gedf2',compare_parts='__fpcmp_parts_d',signed='__fixdfsi',subtract='__subdf3',fifo='open_cfw_gx8002_uart_fifo_depth',irq='open_cfw_gx8002_request_irq')
    s={k:sy[v] for k,v in names.items()};helpers={s[k]:k for k in ('uint','divide','multiply','add','fix','fifo','irq')};cases=0
    for port,clock,encoding in product(range(2),(0,1,0x1ffffff,0x8000000,0xffffffff) if decoded_frequency else (0,24000000,0xffffffff),(0,1,8,128)):
        base=sy['open_cfw_gx8002_uart_descriptors']+128*port
        d=list(struct.unpack_from('<32I',data,base-section['address']));d[3]=clock
        device=d[1];regs={device+off:0 for off in range(0,256,4)};regs[device+244]=encoding<<16
        if initialize:
            from verify_gx8002_uart_initialize import execute as init_execute
            configured_results=[]
            def configure_hook(pointer,init_trace):
                if pointer!=base:raise ValueError('Initializer descriptor handoff')
                for item in init_trace:
                    if item[0]=='write':d[(item[1]-base)//4]=item[2]
                result,memory,trace=execute(code,sy['open_cfw_gx8002_uart_configure'],d,regs,helpers,arithmetic(code,s),0,
                    fifo_hook=lambda dev,param:fifo(code,s['fifo'],dev,param,base),
                    irq_hook=lambda number,handler,private:irq(code,s['irq'],number,handler,private,sy['open_cfw_gx8002_irq_enable']),descriptor_base=base)
                configured_results.append((result,memory,trace));return result
            helper_map={sy['open_cfw_gx8002_'+name]:kind for name,kind in (('platform_gate','gate'),('clock_frequency','frequency'),('uart_configure','configure'))}
            init_result,_=init_execute(code,sy['open_cfw_gx8002_uart_initialize'],port,115200,clock,0,helper_map,configure_hook,gate_hook=gate_hook,frequency_hook=frequency_hook if decoded_frequency else None)
            if init_result or len(configured_results)!=1:raise ValueError('Initializer configuration return')
            result,memory,trace=configured_results[0]
            clock=d[3]
        else:
            result,memory,trace=execute(code,sy['open_cfw_gx8002_uart_configure'],d,regs,helpers,arithmetic(code,s),0,
                fifo_hook=lambda dev,param:fifo(code,s['fifo'],dev,param,base),
                irq_hook=lambda number,handler,private:irq(code,s['irq'],number,handler,private,sy['open_cfw_gx8002_irq_enable']),descriptor_base=base)
        divisor,remainder=divmod(clock,115200*16)
        if result or memory[base+20]!=divisor or memory[base+24]!=int(remainder/(115200*16)*16+0.5):raise ValueError('Owned default baud')
        if memory[base+48]!=encoding*16 or memory[base+56]!=1 or memory[base+52]!=0:raise ValueError('Owned default FIFO')
        slot=sy['open_cfw_gx8002_irq_table']+(6+port)*8
        if memory[slot]!=sy['open_cfw_gx8002_uart_interrupt'] or memory[slot+4]!=base:raise ValueError('Owned descriptor IRQ pointer')
        if any(x[0] in ('read','write') and 0x20026a94<=x[1]<0x20026b94 for x in trace):raise ValueError('Retained UART descriptor access')
        # Execute application start calls against the actual configuration output.
        from verify_gx8002_uart_receive_control import execute as receive_start
        from verify_gx8002_uart_transmit_control import execute as transmit_start
        from verify_gx8002_uart_receive_irq import irq_execute
        for direction,control,callback,private,bit in (
                ('receive',receive_start,0x10300000,0x1234,1),
                ('transmit',transmit_start,0x10300010,0x5678,2)):
            state=[0x140];transitions=[];before=dict(memory)
            def control_irq(save,argument):
                target=sy['open_cfw_gx8002_irq_save' if save else 'open_cfw_gx8002_irq_restore']
                value,state[0]=irq_execute(code,target,state[0],argument)
                transitions.append(state[0]);return value
            result,control_trace,memory=control(code,sy['open_cfw_gx8002_uart_'+direction+'_start'],
                'start',port,callback,private,memory[device+4],state[0],irq_hook=control_irq,
                descriptor_base=sy['open_cfw_gx8002_uart_descriptors'],
                save_entry=sy['open_cfw_gx8002_irq_save'],restore_entry=sy['open_cfw_gx8002_irq_restore'],
                initial_memory=memory)
            expected_memory=dict(before)
            for offset,value in (((64,1),(80,callback),(84,private)) if bit==1 else ((68,1),(72,callback),(76,private))):
                expected_memory[base+offset]=value
            expected_memory[device+4]=before[device+4]|bit
            if result or memory!=expected_memory or transitions!=[0x100,0x140]:
                raise ValueError('Configured UART start state or IRQ restoration')
            control_calls+=1
        memory[device+8]=6;memory[device+132]=5;memory[device+128]=3
        configured=[memory[base+i*4] for i in range(32)]
        peripherals={address:value for address,value in memory.items() if address>=0xa0000000}
        calls=[]
        def handler_call(target,number,private):
            if (target,number,private)!=(memory[slot],6+port,memory[slot+4]):raise ValueError('Configured dispatch arguments')
            calls.append(interrupt(code,target,configured,peripherals,descriptor_base=private))
        dispatch_trace=dispatch(code,sy['open_cfw_gx8002_irq_dispatch_body'],38+port,memory[slot],memory[slot+4],table_address=sy['open_cfw_gx8002_irq_table'],handler_hook=handler_call)
        if len(calls)!=1 or calls[0][0]:raise ValueError('Configured handler return')
        callbacks=[item for item in calls[0][2] if item[0]=='callback']
        expected=[('callback',0x10300000,port,5,0x1234),('callback',0x10300010,port,(encoding*16-3)&0xffffffff,0x5678)]
        if callbacks!=expected:raise ValueError('Configured handler callbacks')
        if dispatch_trace[-1]!=('handler',memory[slot],6+port,base):raise ValueError('Configured IRQ table handoff')
        cases+=1
    return {'candidate':candidate,'decoded_control_calls':control_calls,'decoded_frequency_calls':frequency_calls,'decoded_gate_calls':gate_calls,'initialization_composed':initialize,'cases':cases,'dispatched_handlers':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Loads compiled source data into a modeled address space; this is not startup copy execution. Clock results are modeled unless decoded_frequency is enabled; that mode executes five fixed-selector DTO/divider patterns. Peripheral stimuli and callback addresses are harness inputs; decoded receive/transmit starts install callbacks into configuration output with decoded IRQ save/restore. Configuration table output feeds decoded dispatch and relocated handler. Decoded configuration/FIFO/IRQ and arithmetic helpers use separate frames.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-owned-defaults.json').write_text(json.dumps(r,indent=2)+'\n');print('Owned UART default cases:',r['cases'])
