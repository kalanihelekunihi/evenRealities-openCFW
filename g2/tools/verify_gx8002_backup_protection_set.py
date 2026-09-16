# SPDX-License-Identifier: MIT
"""Decoded backup protection setter: ordered reads, writes and helper effects."""
import json, subprocess
from itertools import product
from build_gx8002_backup_protection_set import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_backup_protection_set import execute

def verify():
    evidence=build()
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x3f92c','--stop-address=0x3fa38',str(path)],text=True))
    old={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez','bnezad'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        old[pc+delta]=(op,args,width)
    new=decode((ROOT/'build/gx8002-backup-protection-set/erase-linked.disassembly.txt').read_text())
    cases=0
    for present,manufacturer,requested,count,status,result,delay in product((0,1,2),(0,0x5e,0x85,0x805e),(0,1,4095,4096,8192,0xffffffff),(0,1,3),(0,0x55,0xff),(0,4096,0xffffffff),(0,2)):
        memory={};output=0x20044000
        word(memory,output,0xa5a5a5a5);word(memory,0x20016d6c,0x20041000)
        for device in (0x20041000,0x20041100):
            word(memory,device+16,0x20042000 if present else 0)
            word(memory,device+4,manufacturer<<16)
        word(memory,0x20042000,0x20043000 if present==2 else 0);word(memory,0x20042004,count)
        rows=[(0,3,0,12,0),(1,3,4,12,4096),(2,3,8,12,8192)]
        selected=(0,0,0,0,0)
        for i,row in enumerate(rows):
            for j,v in enumerate(row[:4]):memory[0x20043000+i*8+j]=v
            word(memory,0x20043004+i*8,row[4])
        for row in rows[:count]:
            if requested<row[4]:break
            selected=row
        want=(0xffffffff if requested else 0) if present!=2 else 0xffffffff if manufacturer not in (0x5e,0x85) or result==0xffffffff else 0
        snapshots=[]
        for code in (old,new):
            calls=[];phase=[0];poll=[0]
            def callback(target,args,state,events):
                calls.append(target)
                if target==0x10006c30:
                    assert args[2]==1
                    if phase[0] in (0,4):
                        assert args[0]==5
                        value=1 if poll[0]<delay else 0;poll[0]+=1
                        if not value:
                            if phase[0]==0:word(state,0x20016d6c,0x20041100)
                            phase[0]+=1;poll[0]=0
                    else:
                        assert phase[0] in (1,2) and args[0]==(5 if phase[0]==1 else 0x35)
                        value=status if phase[0]==1 else status^0xff;phase[0]+=1
                    state[args[1]]=value;events.append(('command',args[0],value));return 0xffffffff
                if target==0x10006d34:
                    assert phase[0]==3 and args[1:3]==[2,1]
                    a,b,c,d,_=selected
                    payload=[state[args[0]],state[args[0]+1]]
                    assert payload==[((status&~b)|a)&255,(((status^0xff)&~d)|c)&255]
                    events.append(('status_write',payload));phase[0]=4;return 0xffffffff
                assert target==0x10006f04 and phase[0]==5
                events.append(('query',result));phase[0]=6;return result
            outcome,after,events=execute(code,0x10006fec,[requested,output],memory,callback)
            assert outcome[:2]==('return',want)
            expected_output=result if present==2 and manufacturer in (0x5e,0x85) and result!=0xffffffff else 0
            assert sum(after[output+i]<<(8*i) for i in range(4))==expected_output
            assert phase[0]==(0 if present!=2 else 1 if manufacturer not in (0x5e,0x85) else 6)
            snapshots.append((outcome[:2],after,events))
        assert snapshots[0]==snapshots[1],(present,manufacturer,requested,count,status,result,delay,snapshots)
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Read transport, status-write and final query modeled.','Finite three-entry tables; ordinary output pointer; hardware and full composition unqualified.']}
    (ROOT/'docs/research/gx8002-backup-protection-set-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(verify()['cases'])
