# SPDX-License-Identifier: MIT
import json
from itertools import product
from link_gx8002_uart_configure_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from compare_gx8002_irq_dispatch import execute as dispatch
from execute_gx8002_uart_interrupt import execute as interrupt


def verify():
    candidate=build();path=ROOT/'build/gx8002-uart-configure-source/uart.elf';elf=Elf32(path.read_bytes(),str(path))
    symbols={s['name']:s['value'] for s in elf.symbols() if s['name']};code=decode((path.parent/'uart.disassembly.txt').read_text())
    handler=symbols['open_cfw_gx8002_uart_interrupt'];table=symbols['open_cfw_gx8002_irq_table'];start=symbols['open_cfw_gx8002_irq_dispatch_body'];cases=0
    for irq,upper,pending in product((6,7,31),(0,0x200,0xfffffe00),range(8)):
        base=0x20026a94;device=0xa0100000
        d=[0]*32;d[0]=irq-6;d[1]=device;d[16]=d[17]=1;d[20]=0x10300000;d[18]=0x10300010;d[21]=0x1234;d[19]=0x5678
        regs={device+off:0 for off in range(0,256,4)};regs[device+8]=pending;regs[device+0x84]=9;regs[device+0x80]=3;regs[device+0xf4]=1<<16
        results=[]
        def call(target,number,private):
            if (target,number,private)!=(handler,irq,base):raise ValueError('Dispatch UART arguments')
            results.append(interrupt(code,target,d,regs))
        status=upper|(irq+32)
        trace=dispatch(code,start,status,handler,base,table_address=table,handler_hook=call)
        if trace!=[('read',0xe000ec00,status),('read',table+irq*8,handler),('read',table+irq*8+4,base),('handler',handler,irq,base)]:raise ValueError('Relocated dispatch trace')
        if len(results)!=1 or results[0][0]!=0:raise ValueError('UART dispatch return')
        wanted=[]
        if pending&4:wanted.append(('callback',d[20],d[0],9,d[21]))
        if pending&2:wanted.append(('callback',d[18],d[0],13,d[19]))
        if [x for x in results[0][2] if x[0]=='callback']!=wanted:raise ValueError('Dispatched UART callbacks')
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Decoded dispatcher body calls relocated UART handler in a separate decoded frame. Active IRQ status and table reads supplied by harness. Does not exercise hardware entry context, startup or nested interrupts. Ready callback bodies modeled.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-dispatch-composition.json').write_text(json.dumps(r,indent=2)+'\n');print('UART dispatch composition cases:',r['cases'])
