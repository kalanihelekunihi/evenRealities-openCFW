# SPDX-License-Identifier: MIT
"""Decoded callback differential baseline, including version tokenization."""
import json,subprocess
from itertools import product
from oracle_gx8002_app_command_callback import expected
from build_gx8002_app_command_callback import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_app_command_callback import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
PACKET,DATA,STATE,REPLY=0x20040000,0x20041000,0x2002e8f0,0x20026d5c

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x129bc','--stop-address=0x12c88',str(path)],text=True));new=decode((ROOT/'build/gx8002-app-command-callback/candidate.disassembly.txt').read_text());cases=0
    hits=0
    for command,stage,field,value in product((258,263,265,266,267,268,269,270,271,368,369),(0x10206c24,0x102093f4,0x10207404,0x10206908,0x10205f24,0x10207a80,0x102043ac,0x102065dc,0x102049b0),(PACKET+4,PACKET+24,STATE+40,STATE+56,DATA),(0,1,2,271)):
        length=3;gain=12;result=0xffffffff
        m={a+i:0xa5 for a,n in ((PACKET,28),(DATA,8),(STATE,68),(REPLY,28)) for i in range(n)}
        for a,v in ((PACKET+4,command),(PACKET+16,DATA),(PACKET+24,length),(STATE+40,0),(STATE+56,gain)):word(m,a,v)
        for i in range(8):m[DATA+i]=(gain+i)&255
        runs=[];hit_runs=[]
        for code,entry in ((old,0x129bc),(new,0x10209430)):
            token=[None];hit=[False]
            def modeled_helper(t,a,mem,events,sp):
                if t==0x1020995c:
                    start=a[0] or token[0]
                    if start is None:raise ValueError('Tokenizer state')
                    end=start
                    while mem[end] not in (0,46):end+=1
                    token[0]=end+1 if mem[end]==46 else None;mem[end]=0
                    events.append(('token',bytes(mem[i] for i in range(start,end))));return start
                if t==0x10206c24:
                    count=1 if a[0] in (0x1020b7bd,0x1020b7c4,0x1020b7dd,0x1020b7f3,0x1020b8a9) else 0
                    events.append(('print',*a[:count+1]));return result
                if t==0x102083bc:
                    pointer=word(mem,REPLY+16);size=word(mem,REPLY+24)
                    events.append(('enqueue',mem[REPLY+4]|mem[REPLY+5]<<8,mem[REPLY+7],bytes(mem[pointer+i] for i in range(size))));return result
                arities={0x102093f4:3,0x10207404:1,0x10206908:0,0x10205f24:2,0x10207a80:0,0x102043ac:2,0x102065dc:2,0x102049b0:2}
                events.append((hex(t),*a[:arities[t]]));return result
            def helper(t,a,mem,events,sp):
                answer=modeled_helper(t,a,mem,events,sp)
                if t==stage and not hit[0]:
                    hit[0]=True
                    if field==DATA:mem[field]=value&255
                    else:word(mem,field,value if field!=PACKET+24 else value%4)
                return answer
            ret,actual,events=execute(code,entry,[PACKET],m,helper)
            runs.append((ret,actual,events));hit_runs.append(hit[0])
        if runs[0]!=runs[1]:raise ValueError(('Callback mismatch',command,length,gain,result,runs))
        cases+=1;hits+=hit_runs[0]
        if hit_runs[0]!=hit_runs[1]:raise ValueError("Mutation reach mismatch")
    return {'candidate':candidate,'cases':cases,'cases_reaching_mutation':hits,'source_admitted':False,'limits':['Differential one-shot helper mutations across command, length, microphone cache, gain and payload bytes; nested behavior remains unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-app-command-callback-mutations.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
