# SPDX-License-Identifier: MIT
"""Exercise the drain wait using compiled source descriptor defaults."""
import json,struct
from itertools import product
from link_gx8002_uart_configure_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_flush import execute


def verify():
    candidate=build();path=ROOT/'build/gx8002-uart-configure-source/uart.elf'
    elf=Elf32(path.read_bytes(),str(path));symbols={s['name']:s for s in elf.symbols() if s['name']}
    descriptor=symbols['open_cfw_gx8002_uart_descriptors'];section=elf.sections[descriptor['section']]
    data=elf.contents(section);table=descriptor['value'];entry=symbols['open_cfw_gx8002_uart_flush']['value']
    code=decode((path.parent/'uart.disassembly.txt').read_text());cases=0
    for port,delay,waiting,ready in product((0,1),(0,1,3,32,128),(0,1,32,0xffffffbf),(64,65,0xffffffff,None)):
        device=struct.unpack_from('<I',data,table-section['address']+port*128+4)[0]
        statuses=[waiting]*delay+([] if ready is None else [ready])
        result=execute(code,entry,port,statuses,descriptor_base=table,device_base=device)
        expected=(ready is not None,[('read',table+port*128+4,device)]+[('read',device+20,x) for x in statuses])
        if result!=expected:raise ValueError('Relocated flush descriptor/MMIO contract')
        if any(0x20026a94<=x[1]<0x20026b94 for x in result[1]):raise ValueError('Stock UART storage access')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Compiled source data supplied to modeled memory; startup copy and physical UART behavior remain unqualified. Finite stalled prefixes do not bound the firmware wait.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-flush-relocated.json').write_text(json.dumps(r,indent=2)+'\n');print('Relocated flush cases:',r['decoded_cases'])
