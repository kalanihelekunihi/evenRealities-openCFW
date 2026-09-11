# SPDX-License-Identifier: MIT
"""Verify linked buffer transmit using source descriptor defaults."""
import json,struct
from itertools import product
from link_gx8002_uart_configure_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_write import execute,signed
from compare_gx8002_uart_transmit import execute as transmit


def verify():
    candidate=build();path=ROOT/'build/gx8002-uart-configure-source/uart.elf'
    elf=Elf32(path.read_bytes(),str(path));sy={s['name']:s for s in elf.symbols() if s['name']}
    table=sy['open_cfw_gx8002_uart_descriptors'];section=elf.sections[table['section']];data=elf.contents(section)
    read=sy['open_cfw_gx8002_uart_write'];helper=sy['open_cfw_gx8002_uart_transmit']['value']
    code=decode((path.parent/'uart.disassembly.txt').read_text())
    targets={int(args,0) for pc,(op,args,width) in code.items() if read['value']<=pc<read['value']+read['size'] and op=='bsr'}
    if targets!={helper}:raise ValueError('Write helper relocation')
    cases=0;stalled=0
    for port,length,delay,stall in product((0,1),(0,1,2,16,0xffffffff,0x80000000),(0,3,32),(None,0,1)):
        descriptor=table['value']+port*128;device=struct.unpack_from('<I',data,descriptor-section['address']+4)[0]
        count=max(0,signed(length));values=[(127+i*37)&255 for i in range(count)];buffer=0x200a0000
        def send(pointer,value,index):
            if pointer!=descriptor:raise ValueError('Write descriptor relocation')
            status,trace=transmit(code,helper,pointer,device,value,[64]*delay+([] if index==stall else [33]))
            return status=='returned',trace
        result=execute(code,read['value'],port,buffer,length,values,helper,transmit_hook=send)
        expected=[];returned=count
        for i,value in enumerate(values):
            expected.extend([('read_byte',buffer+i,value),('transmit',descriptor,value),('read',descriptor+4,4,device)])
            expected.extend([('read',device+20,4,64)]*delay)
            if i==stall:returned=None;stalled+=1;break
            expected.extend([('read',device+20,4,33),('write',device,4,value)])
        if result!=(returned,expected):raise ValueError('Relocated nested send contract')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'stalled_prefixes':stalled,'source_admitted':False,'hardware_qualified':False,'limits':['Actual linked instructions and compiled defaults in separate interpreter frames. Peripheral stimuli modeled; startup and complete firmware integration unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-write-relocated.json').write_text(json.dumps(r,indent=2)+'\n');print('Relocated write cases:',r['decoded_cases'])
