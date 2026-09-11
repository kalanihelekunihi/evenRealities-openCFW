# SPDX-License-Identifier: MIT
import json
from itertools import product
from link_gx8002_uart_configure_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_initialize import execute


def verify():
    candidate=build(include_initialize=True);path=ROOT/'build/gx8002-uart-initialize-source/uart.elf';elf=Elf32(path.read_bytes(),str(path))
    sy={s['name']:s['value'] for s in elf.symbols() if s['name']};code=decode((path.parent/'uart.disassembly.txt').read_text())
    helpers={sy['open_cfw_gx8002_'+name]:kind for name,kind in (('platform_gate','gate'),('clock_frequency','frequency'),('uart_configure','configure'))}
    clocks={0,1,0xffffffff}
    clocks.update(base+off for base in (0,1000000,24000000,4294000000) for off in (0,99,100,101,999899,999900,999901,999999) if base+off<=0xffffffff)
    cases=0
    for port,baud,clock,status in product((0,1,2,0xffffffff),(0,115200,0xffffffff),sorted(clocks),(0,7,0xffffffff)):
        remainder=clock%1000000;rounded=clock-remainder if remainder<=100 else clock+1000000-remainder if remainder>=999900 else clock
        pointer=sy['open_cfw_gx8002_uart_descriptors']+128*port
        wanted=(0xffffffff,[]) if port>=2 else (status,[('gate',17+port,1),('frequency',16),('write',pointer+12,rounded&0xffffffff),('write',pointer+16,baud),('configure',pointer)])
        result=execute(code,sy['open_cfw_gx8002_uart_initialize'],port,baud,clock,status,helpers)
        if result!=wanted:raise ValueError(('Relocated initialization',port,baud,clock,status,result,wanted))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Relocated initializer instructions and call addresses checked; clock and configuration helper results modeled here. Does not qualify startup or full initialization dependency execution.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-initialize-relocated.json').write_text(json.dumps(r,indent=2)+'\n');print('Relocated initialization cases:',r['cases'])
