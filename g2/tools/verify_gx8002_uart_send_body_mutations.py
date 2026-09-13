# SPDX-License-Identifier: MIT
"""Compare complete decoded sender across synchronous helper mutations."""
import json,subprocess
from itertools import product
from verify_gx8002_uart_send_body_complete import execute,build,ROOT,word,decode,BASE

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x110c4','--stop-address=0x111dc',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-uart-message-body/buffers.disassembly.txt').read_text());cases=0
    for port,count,total,space,target,field,value in product((0,1),(0,1,16),(33,64),(1,16),(0x10203604,0x10203664,0x10203720),('sent','needed','body','available'),(0,1,16,0xffffffff)):
        packet=0x20040000;available=0x20041000;sent=0x2002e348+port*4;needed=0x2002e350+port*4
        memory={BASE+i:0 for i in range(800)};memory.update({packet+i:0 for i in range(32)});memory.update({available+i:0 for i in range(4)})
        for address,item in ((sent,count),(needed,total),(packet+24,total),(packet+16,0x20050000),(available,space)):word(memory,address,item)
        destination={'sent':sent,'needed':needed,'body':packet+16,'available':available}[field]
        def mutate(helper,mem):
            if helper==target:word(mem,destination,value)
        a=execute(old,0x110c4,port,packet,available,memory,mutation=mutate);b=execute(new,0x10207b38,port,packet,available,memory,mutation=mutate)
        if a!=b:raise ValueError(('Mutation',port,count,total,space,hex(target),field,value,a,b))
        cases+=1
    alias_cases=0
    for port,count,total,space,alias in product((0,1),(0,1,16),(0,33,64),(0,1,16),('sent','needed','body','length','context')):
        packet=0x20040000;sent=0x2002e348+port*4;needed=0x2002e350+port*4
        available={'sent':sent,'needed':needed,'body':packet+16,'length':packet+24,'context':BASE+port*380+372}[alias]
        memory={BASE+i:0 for i in range(800)};memory.update({packet+i:0 for i in range(32)})
        for address,item in ((sent,count),(needed,total),(packet+24,total),(packet+16,0x20050000),(available,space)):word(memory,address,item)
        a=execute(old,0x110c4,port,packet,available,memory);b=execute(new,0x10207b38,port,packet,available,memory)
        if a!=b:raise ValueError(('Alias',port,count,total,space,alias,a[0],b[0],a[2],b[2]))
        alias_cases+=1
    null_cases=0
    for port,count,total,packet,available in product((0,1),(0,1,16),(0,1,64),(0,0x20040000),(0,0x20041000)):
        if packet and available:continue
        sent=0x2002e348+port*4;needed=0x2002e350+port*4
        memory={BASE+i:0 for i in range(800)}
        if packet:
            memory.update({packet+i:0 for i in range(32)});word(memory,packet+24,total)
        if available:
            memory.update({available+i:0 for i in range(4)});word(memory,available,16)
        word(memory,sent,count);word(memory,needed,total)
        outcomes=[]
        for code,entry in ((old,0x110c4),(new,0x10207b38)):
            try:outcomes.append(execute(code,entry,port,packet,available,memory))
            except KeyError as error:outcomes.append(('unmapped_read',error.args[0]))
        if outcomes[0]!=outcomes[1]:raise ValueError(('Null mismatch',port,count,total,packet,available))
        if not packet and count==0:
            if outcomes[0]!=('unmapped_read',24):raise ValueError('Expected prevalidation length read')
        else:
            expected_result=1 if count==total else 0xffffffff
            if outcomes[0][0]!=('return',expected_result):raise ValueError('Null branch result')
        null_cases+=1
    return {'candidate':candidate,'decoded_mutation_cases':cases,'decoded_alias_cases':alias_cases,'decoded_null_cases':null_cases,'source_admitted':False,'limits':['Synchronous write/stop/async helpers mutate selected progress, body-address or budget words. Compared full stock/source outcomes and ordered calls/writes; not hardware or arbitrary concurrency qualification.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-send-body-mutations.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_mutation_cases'])
