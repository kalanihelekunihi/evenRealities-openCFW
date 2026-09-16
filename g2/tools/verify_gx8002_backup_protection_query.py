# SPDX-License-Identifier: MIT
"""Decoded backup protection callback ABI, output writes and forwarding."""
import json, subprocess
from itertools import product
from build_gx8002_backup_protection_query import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_backup_protection_query import execute

def verify():
    evidence=build()
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x3f844','--stop-address=0x3f8ec',str(path)],text=True))
    old={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez','bnezad'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        old[pc+delta]=(op,args,width)
    new=decode((ROOT/'build/gx8002-backup-protection-query/erase-linked.disassembly.txt').read_text())
    cases=0
    for present,manufacturer,first,second,count,delay in product((0,1,2),(0,0x5e,0x85,0x805e),range(256),(0,1,0xaa,0xff),(0,1,3),(0,2)):
        memory={};word(memory,0x20016d6c,0x20041000)
        for device in (0x20041000,0x20041100,0x20041200):
            word(memory,device+16,0x20042000 if present else 0)
            word(memory,device+4,manufacturer<<16)
        word(memory,0x20042000,0x20043000 if present==2 else 0)
        word(memory,0x20042004,count)
        rows=[(0,1,0,1,0),(1,1,0,0,4096),(0,0,0,0,0xffffffff)]
        for i,row in enumerate(rows):
            for j,v in enumerate(row[:4]):memory[0x20043000+i*8+j]=v
            word(memory,0x20043004+i*8,row[4])
        want=0xffffffff
        if present==2 and manufacturer in (0x5e,0x85):
            for a,b,c,d,length in rows[:count]:
                if first&b==a and second&d==c:want=length;break
        snapshots=[]
        for code in (old,new):
            calls=[]
            def callback(target,args,state,events):
                index=len(calls)
                assert target==0x10006c30 and args[2]==1
                assert 0x2006ffc0<=args[1]<0x20070000
                opcode=5 if index<=delay+1 else 0x35
                value=1 if index<delay else 0 if index==delay else first if index==delay+1 else second
                assert args[0]==opcode and index<=delay+2
                state[args[1]]=value
                # Distinct selected-device pointers require the documented reloads.
                if index==delay:word(state,0x20016d6c,0x20041100)
                if index==delay+2:word(state,0x20016d6c,0x20041200)
                calls.append(opcode);events.append(('command',opcode,value))
                return 0xffffffff
            outcome,after,events=execute(code,0x10006f04,[],memory,callback)
            assert outcome[:2]==('return',want),(present,manufacturer,first,second,count,delay,outcome,want)
            assert len(calls)==(0 if present!=2 else delay+1+(2 if manufacturer in (0x5e,0x85) else 0))
            snapshots.append((outcome[:2],after,events))
        assert snapshots[0]==snapshots[1]
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Command transport writes modeled bytes and returns an ignored failure code; physical transport not executed.','Finite three-entry tables and readiness delays; candidate stack frame is four bytes larger than stock.']}
    (ROOT/'docs/research/gx8002-backup-protection-query-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(verify()['cases'])
