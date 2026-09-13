# SPDX-License-Identifier: MIT
"""Initialization mutation and configuration/context overlap comparisons."""
import json,subprocess
from itertools import product
from verify_gx8002_uart_message_initialize import helper_for,oracle
from execute_gx8002_uart_message_initialize import execute,word,BASE,MASK
from build_gx8002_uart_message_initialize import ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x119e4','--stop-address=0x11ad8',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-uart-message-initialize/callback.disassembly.txt').read_text());cases=0
    for port,alias,target,value,field in product((0,1),(-1,0,4,8,12,16,28),(0x10207ac0,0x102036e8,0x10203704,0x10203530,0x10206f9c,0x1020368c,0x102076c0,0x10207718,0x10207770),(0,1,MASK),range(5)):
        ctx=BASE+380*port;config=0x20040000 if alias<0 else ctx+alias
        m={BASE+i:0 for i in range(760)};m.update({0x2002ecc4+i:0xa5 for i in range(20)})
        for i,v in enumerate((port,115200,0,1)):word(m,config+4*i,v)
        address=(ctx+8,ctx+12,ctx+16,config+8,BASE+(1-port)*380+12)[field]
        def fresh():
            base=helper_for(0);fired=[False]
            def helper(t,args,memory,events):
                result=base(t,args,memory,events)
                if t==target and not fired[0]:word(memory,address,value);fired[0]=True
                return result
            return helper
        expected=oracle(m,config,fresh())
        for code,entry in ((old,0x119e4),(new,0x10208458)):
            a=execute(code,entry,config,0,m,fresh());actual=(a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])
            if actual!=expected:raise ValueError(('Initialization mutation',port,alias,hex(target),value,field,hex(entry),actual[2],expected[2]))
        cases+=1
    return {'decoded_mutation_alias_cases':cases,'source_admitted':False,'limits':['Selected aligned configuration/context overlaps and one helper mutation per execution. Physical helper behavior and arbitrary overlap/concurrency unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-message-initialize-mutations.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
