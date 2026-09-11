# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from verify_gx8002_uart_transmit_complete import verify as complete_verify,execute as complete,ROOT,decode
from verify_gx8002_dma_release import verify as release_verify,execute as release
from verify_gx8002_dma_deallocate import execute as deallocate,expected
from build_gx8002_uart_flush import build as build_flush
from verify_gx8002_uart_flush import execute as flush
from link_gx8002_irq import link
from verify_gx8002_uart_receive_irq import irq_execute
from verify_gx8002_dma_uart_clock_link import execute as gate_execute,build as build_gate_cluster,Elf32,oracle

def verify():
    completion=complete_verify();release_dependency=release_verify();drain=build_flush();irq=link()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    gate_link=build_gate_cluster();gate_path=ROOT/'build/gx8002-dma-uart-source/dma-uart.elf'
    gate_elf=Elf32(gate_path.read_bytes(),str(gate_path));sy={s['name']:s for s in gate_elf.symbols() if s['name']}
    data=next(s for s in gate_elf.sections if s['name']=='.data');ro=next(s for s in gate_elf.sections if s['name']=='.rodata')
    table_base=sy['gx_clock_param_table']['value'];offset=table_base-data['address']
    table=gate_elf.contents(data)[offset:offset+416];jumps=gate_elf.contents(ro)
    gate_code=decode((gate_path.parent/'dma-uart.disassembly.txt').read_text());gate_calls=0
    new_irq=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-irq/irq.elf')],text=True))
    new=decode((ROOT/'build/gx8002-uart-transmit-complete/complete.disassembly.txt').read_text())
    new_flush=decode((ROOT/'build/gx8002-uart-flush/flush.disassembly.txt').read_text())
    new_release=decode((ROOT/'build/gx8002-dma-release/release.disassembly.txt').read_text())
    new_free=decode((ROOT/'build/gx8002-dma-deallocate/deallocate.disassembly.txt').read_text());cases=0
    for outer,leaf,channel,allocation,delay,ready,token,register in product((False,True),(False,True),(0,1),([1,1],[1,0],[0,1],[2,255]),(0,3,32),(64,None),(0,0x40,0x80000040,0xffffffff),(0,0xffffffff,0x55555555)):
        events=[];state=[token];transitions=[]
        def irq_hook(save,argument):
            entry=(0x10025560 if save else 0x1002556c) if leaf else (0x17574 if save else 0x17580)
            value,state[0]=irq_execute(new_irq if leaf else old,entry,state[0],argument)
            transitions.append(state[0]);return value
        def gate_hook(module,enabled):
            nonlocal gate_calls
            if state[0]!=token&~0x40:raise ValueError('Completion gate exclusion')
            if (module,enabled)!=(25,0):raise ValueError('Completion clock arguments')
            result=gate_execute(gate_code,sy['open_cfw_gx8002_platform_gate']['value'],jumps,table,module,enabled,register,0,table_base,ro['address'],sy['__module_get_info']['value'])
            if result!=oracle(table,module,enabled,register):raise ValueError('Completion decoded clock effects')
            gate_calls+=1

        def release_hook(number):
            def deallocate_hook(value):return deallocate(new_free if leaf else old,0x10203a98 if leaf else 0xd024,allocation,token,value,irq_hook=irq_hook,gate_hook=gate_hook)
            result=release(new_release if leaf else old,0x10203b38 if leaf else 0xd0c4,number,deallocate_hook)
            if result!=expected(allocation,token,channel):raise ValueError('Completion release effects')
            events.append('release')
        def flush_hook(port):
            if state[0]!=token or transitions!=[token&~0x40,token]:raise ValueError('IRQ restoration before drain')
            events.append('flush')
            return flush(new_flush if leaf else old,0x10203598 if leaf else 0xcb24,port,[0]*delay+([] if ready is None else [ready]))
        result=complete(new if outer else old,0x102030c4 if outer else 0xc650,channel,1,0x10207ee0,0x12345678,False,release_hook=release_hook,flush_hook=flush_hook)
        if events!=['release','flush']:raise ValueError('Transmit completion helper order')
        callbacks=[x for x in result[0] if x[0]=='callback']
        if callbacks!=([] if ready is None else [('callback',0x10207ee0,1,0x12345678)]):raise ValueError('Drain callback gate')
        if result[1][0x20026b10]!=0xffffffff:raise ValueError('Transmit channel clear')
        cases+=1
    return {'completion':completion,'release_dependency':release_dependency,'drain':drain,'irq':irq,'gate_link':gate_link,'decoded_gate_calls':gate_calls,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Separate descriptor, allocation and drain frames; callback delivery modeled. IRQ leaves decoded with modeled PSR semantics; clock gate and lookup decoded against compiled source tables, with modeled MMIO stimuli. No physical DMA interrupt/coherence proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-transmit-complete-leaves.json').write_text(json.dumps(report,indent=2)+'\n');print('Transmit completion leaf cases:',report['decoded_cases'])
