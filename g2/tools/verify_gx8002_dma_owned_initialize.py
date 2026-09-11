# SPDX-License-Identifier: MIT
"""Execute initialization with source-owned DMA storage and relocated calls."""
import json
from itertools import product
from link_gx8002_dma_uart_source import build,ROOT
from verify_gx8002_dma_initialize import execute,verify as baseline
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from verify_gx8002_dma_uart_clock_link import execute as clock_execute
from compare_gx8002_platform_gate import oracle
from execute_gx8002_linked_irq_registration import execute as irq_execute

def verify():
    original=baseline()
    try:
        report=build(owned_dma=True,owned_irq=True)
        path=ROOT/'build/gx8002-dma-uart-source/dma-uart.elf'
        elf=Elf32(path.read_bytes(),str(path));symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
        def address(name):return symbols['open_cfw_gx8002_'+name]
        state=address('dma_state');code=decode((path.parent/'dma-uart.disassembly.txt').read_text());cases=0
        data=next(s for s in elf.sections if s['name']=='.data');ro=next(s for s in elf.sections if s['name']=='.rodata')
        table_base=symbols['gx_clock_param_table'];offset=table_base-data['address'];table=elf.contents(data)[offset:offset+416]
        registration_cases=0
        for number,handler,private in product((*range(34),0x7fffffff,0x80000000,0xffffffff),(0,address('dma_irq_handler')),(0,0xffffffff)):
            writes=irq_execute(code,address('request_irq'),number,handler,private,address('irq_enable'))
            table_address=address('irq_table')
            wanted=[] if number>=32 or handler==0 else [(table_address+number*8,handler),(table_address+number*8+4,private),(0xe000e100,1<<number)]
            if writes!=wanted:raise ValueError('Linked registration boundary')
            registration_cases+=1
        clock_calls=0;irq_calls=0
        def irq_hook(number,handler,private):
            nonlocal irq_calls
            writes=irq_execute(code,address('request_irq'),number,handler,private,address('irq_enable'))
            table=address('irq_table')
            if writes!=[(table+number*8,handler),(table+number*8+4,private),(0xe000e100,1<<number)]:raise ValueError('Initializer IRQ writes')
            irq_calls+=1
        def gate_hook(module,enable):
            nonlocal clock_calls
            result=clock_execute(code,address('platform_gate'),elf.contents(ro),table,module,enable,0xffffffff,0,table_base,ro['address'],symbols['__module_get_info'])
            if result!=oracle(table,module,enable,0xffffffff):raise ValueError('Initializer clock effects')
            clock_calls+=1
        for seed,base,status in product((0,0xffffffff,0x12345678),(0xa1000000,0xa1001000),(0,1,0xffffffff)):
            trace,memory=execute(code,address('dma_initialize'),seed,base,status,state,address('platform_gate'),address('request_irq'),gate_hook,irq_hook)
            wanted=[('write',state,0xa1000000),('write',state+4,2),('write',state+0x368,(state+23)&~15),('write',state+0x370,0),('write',state+0x36c,(state+455)&~15),('write',state+0x371,0),('gate',25,1),('read',state,base),('write',base+0x398,0)]
            wanted += [('write',base+offset,0xffffffff) for offset in (0x338,0x340,0x348,0x350,0x358)]
            wanted += [('write',base+0x398,1),('gate',25,0),('irq',10,address('dma_irq_handler'),0)]
            if trace!=wanted:raise ValueError('Relocated initialization order')
            for channel in range(2):
                pointer=memory[state+0x368+channel*4];low=state+8+432*channel
                if pointer%16 or not low<=pointer or pointer+416>low+432:raise ValueError('Initialized descriptor pointer escapes storage')
            cases+=1
        return {'baseline':original,'owned_link':report,'decoded_cases':cases,'decoded_clock_calls':clock_calls,'decoded_irq_calls':irq_calls,'registration_boundary_cases':registration_cases,'source_admitted':False,'hardware_qualified':False,'limits':['Clock gate and lookup execute in a separate decoded frame; IRQ registration and VIC enable execute together in a separate decoded frame. Startup BSS zeroing and physical RAM placement not qualified.']}
    finally:
        build()

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-owned-initialize.json').write_text(json.dumps(result,indent=2)+'\n');print('Owned initialization cases:',result['decoded_cases'])
