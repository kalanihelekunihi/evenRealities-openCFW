# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from build_gx8002_uart_interrupt import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_interrupt import execute


def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0xc804','--stop-address=0xc8ec',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-uart-interrupt/interrupt.disassembly.txt').read_text());cases=0
    for length,status,limit in product((0,1,8),(0,1,0xffffffbf),(1,2,16,128)):
        base=0x20026a94;device=0xa0100000;buffer=0x20060000
        d=[0]*32;d[1]=device;d[17]=2;d[29]=buffer;d[30]=length;d[27]=0x10300030
        regs={device+off:0 for off in range(0,256,4)};regs.update({buffer+i:0x76543210 for i in range(0,16,4)})
        regs[device+4]=3;regs[device+8]=2;regs[device+20]=status;regs[device+244]=1<<16
        a=execute(old,0xc804,d,regs,poll_limit=limit);b=execute(new,0x10203278,d,regs,poll_limit=limit)
        if a!=b:raise ValueError('Stalled UART trace mismatch')
        returned,memory,trace=a
        if returned is not None or memory[base+116]!=buffer+length or memory[base+120] or memory[device+4]!=3:raise ValueError('Stalled UART state')
        if any(x[0]=='callback' for x in trace):raise ValueError('Premature transmit completion')
        reads=[x for x in trace if x[0]=='read' and x[1]==device+20]
        if reads!=[('read',device+20,4,status)]*limit:raise ValueError('Stalled UART polling oracle')
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Matched finite execution prefixes at 1, 2, 16 and 128 polling reads. Prefix stop belongs to verifier, not firmware. Does not prove eventual behavior or physical hardware timing.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-interrupt-stall.json').write_text(json.dumps(r,indent=2)+'\n');print('Stalled UART prefix cases:',r['cases'])
