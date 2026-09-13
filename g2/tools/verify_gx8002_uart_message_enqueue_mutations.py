# SPDX-License-Identifier: MIT
"""Enqueue helper mutations and packet/context overlap."""
import json,subprocess
from itertools import product
from verify_gx8002_uart_message_enqueue import helper_for,oracle
from execute_gx8002_uart_message_enqueue import execute,word,BASE,MASK
from build_gx8002_uart_message_enqueue import ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x11948','--stop-address=0x119e4',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-uart-message-enqueue/callback.disassembly.txt').read_text());cases=0
    for port,alias,target,value,field in product((0,1),(-1,0,4,8,12,20,24,28,60),(0x10207008,0x102098a8,0x10025664,0x100261b8),(0,1,255,MASK),range(6)):
        ctx=BASE+380*port;p=0x20040000 if alias<0 else ctx+alias
        m={BASE+i:(i*37)&255 for i in range(760)};m.update({0x20040000+i:0 for i in range(32)})
        word(m,ctx+12,1);word(m,ctx+24,0);word(m,ctx+8,port)
        word(m,p+16,0x20050000);word(m,p+24,17);m[p+20]=port;m[p+7]=1;m[p+4]=1;m[p+5]=1
        addr,size=((p+24,4),(p+7,1),(p+4,2),(ctx+20,1),(ctx+24,4),(ctx+8,4))[field]
        def fresh():
            base=helper_for(0,1,0x12345678)
            def helper(t,args,memory,events):
                result=base(t,args,memory,events)
                if t==target:
                    for i in range(size):memory[addr+i]=(value>>(i*8))&255
                return result
            return helper
        expected=oracle(m,p,fresh())
        for code,entry in ((old,0x11948),(new,0x102083bc)):
            a=execute(code,entry,p,0,m,fresh());actual=(a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])
            if actual!=expected:raise ValueError(('Mutation/alias',port,alias,hex(target),value,field,hex(entry),actual[2],expected[2]))
        cases+=1
    return {'decoded_mutation_alias_cases':cases,'source_admitted':False,'limits':['Selected aligned packet/context overlaps and helper writes checked against independent oracle and stock/source execution. Physical helpers/concurrency and arbitrary overlaps unqualified.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-message-enqueue-mutations.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
