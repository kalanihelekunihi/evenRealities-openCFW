# SPDX-License-Identifier: MIT
"""Nested source queue initialization in message startup."""
import json,re,subprocess
from itertools import product
from verify_gx8002_queue_source import verify as qualify
from verify_gx8002_uart_message_initialize import helper_for,oracle
from execute_gx8002_uart_message_initialize import execute,word,BASE
from build_gx8002_uart_message_initialize import ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    dependency=qualify(ROOT/'build/csky-macos/install/bin',ROOT/'build/upstream-nationalchip-lvp-kws',ROOT/'build/gx8002-queue')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    q=decode(subprocess.check_output([pre,'-d','--section=.text.LvpQueueInit',str(ROOT/'build/gx8002-queue/queue.o')],text=True))
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x119e4','--stop-address=0x11ad8',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-uart-message-initialize/callback.disassembly.txt').read_text());cases=0;calls=0
    for port,first,second in product((0,1),(0,1,0xffffffff),(0,1,0xffffffff)):
        m={BASE+i:0xa5 for i in range(760)};m.update({0x2002ecc4+i:0xa5 for i in range(20)});config=0x20040000
        word(m,BASE+12,first);word(m,BASE+380+12,second)
        for i,v in enumerate((port,115200,0,1)):word(m,config+i*4,v)
        def fresh():
            base=helper_for(0)
            def helper(t,args,memory,events):
                nonlocal calls
                if t!=0x10206f9c:return base(t,args,memory,events)
                events.append(('queue_init',*args));r={'r'+str(i):v for i,v in enumerate(args)};pc=0
                for _ in range(16):
                    op,arg,width=q[pc];p=[s.strip() for s in arg.split(',')]
                    if op=='rts':calls+=1;return r['r0']
                    if op=='divs':
                        if r[p[1]]!=256 or r[p[2]]!=32:raise ValueError('Queue dimensions')
                        r[p[0]]=r[p[1]]//r[p[2]]
                    elif op=='mult':r[p[0]]*=r[p[1]]
                    elif op=='movi':r[p[0]]=int(p[1],0)
                    elif op=='st.w':
                        reg,ptr,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',arg).groups();a=r[ptr]+int(off,0)
                        if any(a+i not in memory for i in range(4)):raise ValueError('Queue bounds')
                        word(memory,a,r[reg])
                    else:raise ValueError('Queue opcode')
                    pc+=width
                raise ValueError('Queue bound')
            return helper
        expected=oracle(m,config,helper_for(0))
        for code,entry in ((old,0x119e4),(new,0x10208458)):
            a=execute(code,entry,config,0,m,fresh())
            if (a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])!=expected:raise ValueError('Nested queue init')
        cases+=1
    return {'queue_dependency':dependency,'initialization_cases':cases,'queue_executions':calls,'source_admitted':False,'limits':['Actual decoded source queue stores share caller descriptor memory; fixed256/32dimensions. Other helpers modeled; physical concurrency unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-message-initialize-queue.json').write_text(json.dumps(r,indent=2)+'\n');print(r['initialization_cases'],r['queue_executions'])
