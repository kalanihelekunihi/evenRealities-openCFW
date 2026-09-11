# SPDX-License-Identifier: MIT
"""Compose receive-control instructions with authenticated upstream PSR leaves."""
import json,subprocess
from itertools import product
from verify_gx8002_uart_receive_control import verify as control,execute,expected,ROOT,decode
from link_gx8002_irq import link


def irq_execute(code,entry,psr,argument):
    r0=argument
    for _ in range(4):
        op,args,width=code[entry]
        if op=='mfcr' and args=='r0, cr<0, 0>':r0=psr
        elif op=='psrclr' and args=='ie':psr&=~0x40
        elif op=='mtcr' and args=='r0, cr<0, 0>':psr=r0
        elif op=='rts':return r0,psr
        else:raise ValueError('Unexpected PSR instruction')
        entry+=width
    raise ValueError('PSR leaf execution bound')


def verify():
    evidence=control();irq=link();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([pre,'-D',str(stock)],text=True))
    new_irq=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-irq/irq.elf')],text=True));cases=0
    for kind,offset in (('start',0xcc18),('stop',0xcc4c)):
        new=decode((ROOT/'build/gx8002-uart-receive-control'/(kind+'.disassembly.txt')).read_text())
        for outer_source,irq_source,port,callback,word,token in product((False,True),(False,True),(0,1),(0,0x10208098),(0,1,0xffffffff),(0,0x40,0x140,0xffffffff)):
            state=[token];transitions=[]
            def hook(save,argument):
                leaf=new_irq if irq_source else old
                entry=(0x10025560 if save else 0x1002556c) if irq_source else (0x17574 if save else 0x17580)
                result,state[0]=irq_execute(leaf,entry,state[0],argument)
                transitions.append(state[0]);return result
            actual=execute(new if outer_source else old,offset+0x101f6a74 if outer_source else offset,kind,port,callback,0x12345678,word,token,irq_hook=hook)
            if actual!=expected(kind,port,callback,0x12345678,word,token):raise ValueError('Composed receive contract')
            wanted=[] if kind=='start' and not callback else [token&~0x40,token]
            if transitions!=wanted or state[0]!=token:raise ValueError('PSR restore contract')
            cases+=1
    return {'receive_control':evidence,'irq':irq,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Separate decoded call frames; architectural PSR semantics modeled. No physical interrupt timing or UART delivery qualification.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-receive-irq.json').write_text(json.dumps(result,indent=2)+'\n');print('Receive IRQ cases:',result['decoded_cases'])
