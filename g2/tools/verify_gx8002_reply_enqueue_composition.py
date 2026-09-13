# SPDX-License-Identifier: MIT
"""Execute staged reply through registered enqueue on compiled packet defaults."""
import json,subprocess
from itertools import product
from verify_gx8002_reply_enqueue_binding import verify as binding,ROOT,sha,Elf32
from execute_gx8002_app_reply import execute as reply
from execute_gx8002_uart_message_enqueue import execute as enqueue,BASE,word
from verify_gx8002_uart_message_enqueue import oracle,helper_for
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=binding();out=ROOT/'build/gx8002-reply-sdk-types';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode((out/'app_reply.disassembly.txt').read_text());path=ROOT/'build/gx8002-source-candidate/uart-message-enqueue/callback.elf'
    queue_code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    elf=Elf32((ROOT/'build/gx8002-reply-defaults/defaults.elf').read_bytes(),'packet');data=elf.contents(next(s for s in elf.sections if s['name']=='.reply_packet'))
    packet=0x20026d5c;value=0x2002e914;cases=0
    for kind,initialized,full,put in product((0,1),(0,1),(0,1),(0,1)):
        memory={BASE+i:0 for i in range(760)};memory.update({packet+i:v for i,v in enumerate(data)});memory[value]=0;memory[value+1]=0
        word(memory,BASE+12,initialized);memory[BASE+20]=255
        expected=dict(memory);expected[value]=0x34;expected[value+1]=0x12;expected[packet+7]=1;word(expected,packet+16,value);expected[packet+4]=0x70;expected[packet+5]=3 if kind else 2;word(expected,packet+24,2)
        hardware=helper_for(full,put,0x87654321)
        expected_result,expected,expected_trace=oracle(expected,packet,hardware)
        calls=[]
        def helper(target,args,state,events):
            assert target==0x102083bc and args[0]==packet
            result,after,trace=enqueue(queue_code,target,packet,0,state,hardware)
            calls.append((result,[e for e in trace if e[0]!='write_byte']))
            state.clear();state.update(after)
            return result[1]
        result,after,trace=reply(code,0x102093f4,[kind,0x70,0x1234],memory,helper)
        assert result==('return',0) and after==expected and calls==[(expected_result,expected_trace)]
        assert word(after,packet)==0x58585542
        cases+=1
    return {'binding':evidence,'cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Staged reply and authenticated registered enqueue execute in separate frames with explicit memory handoff on compiled packet defaults. Independent oracle checks final memory, queue publication snapshots and helper boundaries across full/failed/uninitialized cases.',
                      'UART context lookup, queue leaves, CRC, cache and send trigger remain modeled. Physical transmission and concurrency unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-reply-enqueue-composition.json').write_text(json.dumps(r,indent=2)+'\n');print('Reply through source enqueue:',r['cases'],'cases')
