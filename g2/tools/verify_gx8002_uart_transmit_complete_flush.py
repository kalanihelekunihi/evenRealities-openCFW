# SPDX-License-Identifier: MIT
"""Compose transmit completion with decoded UART drain polling."""
import json,subprocess
from itertools import product
from build_gx8002_uart_transmit_complete import build,ROOT
from build_gx8002_uart_flush import build as build_flush
from verify_gx8002_uart_transmit_complete import execute
from verify_gx8002_uart_flush import execute as flush
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def verify():
    candidate=build();drain=build_flush();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Completion flush identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc650','--stop-address=0xcb40',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-transmit-complete/complete.disassembly.txt').read_text())
    new.update(decode((ROOT/'build/gx8002-uart-flush/flush.disassembly.txt').read_text()))
    cases=0;stalled=0
    for channel,port,delay,ready,mutate in product((0,1,0xffffffff),(0,1),(0,1,32),(64,0xffffffff,None),(False,True)):
        statuses=[0xffffffbf]*delay+([] if ready is None else [ready])
        def run(code,entry,helper):
            return execute(code,entry,channel,port,0x10207ee0,0x12345678,mutate,
                           flush_hook=lambda number:flush(code,helper,number,statuses))
        a=run(old,0xc650,0xcb24);b=run(new,0x102030c4,0x10203598)
        d=0x20026a94;selected=1 if mutate else port;device=0xa0100000+selected*0x1000
        expected=[('read',d+124,channel),('release',channel),('write',d+124,0xffffffff),
                  ('read',d,selected),('flush',selected),('read',d+selected*128+4,device)]
        expected.extend(('read',device+20,value) for value in statuses)
        callback=0x10208098 if mutate and ready is not None else 0x10207ee0
        private=0xabcdef01 if mutate and ready is not None else 0x12345678
        if ready is not None:
            expected.extend([('read',d+108,callback),('read',d+112,private),('read',d,selected),('callback',callback,selected,private)])
        else:stalled+=1
        memory={d+124:0xffffffff,d:selected,d+108:callback,d+112:private}
        if a!=b or a!=(expected,memory):raise ValueError('Completion drain ordering/state contract')
        cases+=1
    return {'candidate':candidate,'drain':drain,'decoded_cases':cases,'stalled_prefixes':stalled,'source_admitted':False,'hardware_qualified':False,'limits':['Release and callback modeled; drain executes decoded instructions with finite MMIO stimuli. Separate interpreter frames. No physical delivery or whole-firmware qualification.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-transmit-complete-flush.json').write_text(json.dumps(r,indent=2)+'\n');print('Completion drain cases:',r['decoded_cases'],'stalled:',r['stalled_prefixes'])
