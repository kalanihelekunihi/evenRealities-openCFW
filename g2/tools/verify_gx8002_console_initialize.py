# SPDX-License-Identifier: MIT
"""Qualify the exact console wrapper with decoded UART initialization."""
import json,subprocess
from itertools import product
from build_gx8002_console_initialize import build,ROOT,sha,IMAGE_SHA,Elf32
from verify_gx8002_uart_initialize import verify as initialize_verify,execute as initialize
from verify_gx8002_memcpy_source import decode


def execute(code,entry,port,baud,clock,status):
    target=0xcabc if entry==0xcd6c else 0x10203530
    expected={0:('push','r15',2),2:('lrw','r3, 0x2002731c',2),4:('st.w','r0, (r3, 0x0)',2),6:('bsr',hex(target),4),10:('pop','r15',2)}
    if any(code[entry+off]!=instruction for off,instruction in expected.items()):raise ValueError('Console initialize wrapper instructions')
    helpers={0xffe2e60c:'gate',0xffe2e79c:'frequency',0xc954:'configure'} if entry==0xcd6c else {0x10025080:'gate',0x10025210:'frequency',0x102033c8:'configure'}
    result,trace=initialize(code,target,port,baud,clock,status,helpers)
    return result,[('write',0x2002731c,port),('initialize',port,baud),*trace]


def verify():
    candidate=build();dependency=initialize_verify();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Console stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xcabc','--stop-address=0xcd7c',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-console-initialize/initialize.disassembly.txt').read_text())
    new.update(decode((ROOT/'build/gx8002-uart-initialize/initialize.disassembly.txt').read_text()))
    cases=0
    for port,baud,clock,status in product((0,1,2,0xffffffff),(0,115200,0xffffffff),(0,99,100,101,999899,999900,999901,24000000,0xffffffff),(0,7,0xffffffff)):
        remainder=clock%1000000
        rounded=clock-remainder if remainder<=100 else clock+1000000-remainder if remainder>=999900 else clock
        prefix=[('write',0x2002731c,port),('initialize',port,baud)]
        pointer=0x20026a94+port*128
        expected=(0xffffffff,prefix) if port>=2 else (status,prefix+[('gate',17+port,1),('frequency',16),('write',pointer+12,rounded&0xffffffff),('write',pointer+16,baud),('configure',pointer)])
        if execute(old,0xcd6c,port,baud,clock,status)!=expected or execute(new,0x102037e0,port,baud,clock,status)!=expected:raise ValueError('Console nested initialization ordering')
        cases+=1
    return {'candidate':candidate,'initialization_dependency':dependency,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,
        'limits':['Exact wrapper instructions and nested decoded initializer checked. Port store is retained on initialization error. Clock and configure helper effects modeled; physical console operation unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-console-initialize-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Console initialize cases:',r['decoded_cases'])
