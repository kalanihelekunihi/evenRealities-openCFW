# SPDX-License-Identifier: MIT
import json
from itertools import product
from link_gx8002_uart_configure_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_receive_irq import irq_execute
from verify_gx8002_uart_receive_control import execute as receive,expected as receive_expected
from verify_gx8002_uart_transmit_control import execute as transmit,expected as transmit_expected


def verify():
    candidate=build();path=ROOT/'build/gx8002-uart-configure-source/uart.elf';elf=Elf32(path.read_bytes(),str(path));sy={s['name']:s['value'] for s in elf.symbols() if s['name']};code=decode((path.parent/'uart.disassembly.txt').read_text())
    table=sy['open_cfw_gx8002_uart_descriptors'];cases=0;irq_calls=0
    def relocate(value):return table+value-0x20026a94 if 0x20026a94<=value<0x20026b94 else value
    for direction,execute,oracle in (('receive',receive,receive_expected),('transmit',transmit,transmit_expected)):
        for kind,port,callback,private,word,token in product(('start','stop'),(0,1),(0,0x10208098),(0,0x12345678),(0,1,0xffffffff),(0,1,0x40,0x140,0x80000000,0xffffffff)):
            wanted,trace,memory=oracle(kind,port,callback,private,word,token)
            expected=(wanted,[tuple(relocate(v) if isinstance(v,int) else v for v in item) for item in trace],{relocate(k):v for k,v in memory.items()})
            state=[token];transitions=[]
            def irq_hook(save,argument):
                nonlocal irq_calls
                result,state[0]=irq_execute(code,sy['open_cfw_gx8002_irq_save' if save else 'open_cfw_gx8002_irq_restore'],state[0],argument)
                transitions.append(state[0]);irq_calls+=1;return result
            result=execute(code,sy['open_cfw_gx8002_uart_'+direction+'_'+kind],kind,port,callback,private,word,token,irq_hook=irq_hook,descriptor_base=table,save_entry=sy['open_cfw_gx8002_irq_save'],restore_entry=sy['open_cfw_gx8002_irq_restore'])
            if result!=expected:raise ValueError(('Relocated UART control',direction,kind,port))
            if state[0]!=token or transitions!=([] if kind=='start' and callback==0 else [token&~0x40,token]):raise ValueError('Relocated control PSR restoration')
            cases+=1
    return {'candidate':candidate,'irq_calls':irq_calls,'cases':cases,'source_admitted':False,'limits':['Relocated controls and descriptor addresses execute; IRQ save/restore instructions execute in separate leaf frames; PSR hardware semantics are modeled. No physical interrupt or firmware integration claim.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-controls-relocated.json').write_text(json.dumps(r,indent=2)+'\n');print('Relocated control cases:',r['cases'])
