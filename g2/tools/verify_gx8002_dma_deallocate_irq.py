# SPDX-License-Identifier: MIT
"""Compose deallocation with decoded PSR save/restore leaves."""
import json,subprocess
from itertools import product
from verify_gx8002_dma_deallocate import execute,expected,verify as verify_deallocate,ROOT,decode
from verify_gx8002_uart_receive_irq import irq_execute
from link_gx8002_irq import link


def verify():
    candidate=verify_deallocate();irq=link();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-dma-deallocate/deallocate.disassembly.txt').read_text())
    leaves=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-irq/irq.elf')],text=True));cases=0
    for outer,leaf,allocation,channel,token in product((False,True),(False,True),product((0,1,2,255),repeat=2),(0,1),(0,0x40,0x140,0x80000000,0xffffffff)):
        state=[token];transitions=[];gates=[]
        def irq_hook(save,argument):
            entry=(0x10025560 if save else 0x1002556c) if leaf else (0x17574 if save else 0x17580)
            value,state[0]=irq_execute(leaves if leaf else old,entry,state[0],argument)
            transitions.append(state[0]);return value
        def gate_hook(module,enabled):
            if state[0]!=token&~0x40:raise ValueError('Gate outside disabled IRQ state')
            gates.append((module,enabled))
        result=execute(new if outer else old,0x10203a98 if outer else 0xd024,allocation,token,channel,gate_hook=gate_hook,irq_hook=irq_hook)
        wanted=expected(allocation,token,channel)
        if result!=wanted or transitions!=[token&~0x40,token]:raise ValueError('Deallocation decoded IRQ contract')
        if gates!=[x[1:] for x in wanted[0] if x[0]=='resource']:raise ValueError('Deallocation gate contract')
        cases+=1
    return {'candidate':candidate,'irq':irq,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Decoded PSR semantics modeled; resource gate effects modeled but required to occur inside interrupt exclusion. Valid two-channel allocations only; no physical concurrency proof.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-dma-deallocate-irq.json').write_text(json.dumps(r,indent=2)+'\n');print('Deallocation IRQ cases:',r['decoded_cases'])
