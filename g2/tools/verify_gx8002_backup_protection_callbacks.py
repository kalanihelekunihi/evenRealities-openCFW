# SPDX-License-Identifier: MIT
"""Decoded backup protection callback ABI, output writes and forwarding."""
import json, subprocess
from itertools import product
from build_gx8002_backup_protection_callbacks import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_backup_protection_callbacks import execute

def verify():
    evidence=build()
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x3f8ec','--stop-address=0x3fa58',str(path)],text=True))
    old={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        old[pc+delta]=(op,args,width)
    new=decode((ROOT/'build/gx8002-backup-protection-callbacks/erase-linked.disassembly.txt').read_text())
    cases=0
    for entry in (0x10006fac,0x10006fc8,0x100070f8,0x10007108):
        for profile_present,value,result in product((False,True),(0,1,0x1000,0x7fffffff,0x80000000,0xffffffff),(0,1,0x80000000,0xffffffff)):
            memory={};output=0x20040000
            word(memory,output,0xa5a5a5a5);word(memory,0x20016d6c,0x20041000)
            word(memory,0x20041010,0x20042000 if profile_present else 0);word(memory,0x20042000,value)
            snapshots=[]
            for code in (old,new):
                calls=[]
                def callback(target,args,state,events):
                    calls.append(target)
                    if entry==0x10006fac:
                        assert target==0x10006f04
                        assert all(state[output+i]==0 for i in range(4))
                    else:
                        assert target==0x10006fec and args[0]==(value if entry==0x100070f8 else 0)
                        assert 0x2006ffc0<=args[1]<0x20070000 and args[1]%4==0
                        word(state,args[1],0x12345678)
                    return result
                outcome,after,events=execute(code,entry,[output if entry==0x10006fac else value],memory,callback)
                want=(0xffffffff if result==0xffffffff else 0) if entry==0x10006fac else (1 if profile_present and value else 0xffffffff) if entry==0x10006fc8 else result
                assert outcome[:2]==('return',want)
                assert len(calls)==(0 if entry==0x10006fc8 else 1)
                expected=memory.copy()
                if entry==0x10006fac:word(expected,output,result)
                assert after==expected
                snapshots.append((outcome[:2],after,events,calls))
            assert snapshots[0]==snapshots[1]
            cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Query and set engines modeled; callbacks alone do not establish source closure.','Finite ordinary output pointers; no hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-protection-callbacks-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(verify()['cases'])
