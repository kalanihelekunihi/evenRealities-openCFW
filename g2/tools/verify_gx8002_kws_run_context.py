# SPDX-License-Identifier: MIT
"""Actual context ring lookup writes feed decoded KWS runner."""
import json,subprocess
from verify_gx8002_kws_run import verify as qualify,expected,ROOT,sha,decode,Elf32
from execute_gx8002_kws_run import execute
from verify_gx8002_context_acquire import execute as lookup

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-source-candidate/context-acquire/context.elf';elf=Elf32(path.read_bytes(),'context');report=json.loads((ROOT/'docs/research/gx8002-context-acquire-verification.json').read_text());section=next(s for s in elf.sections if s['name']=='.text');assert sha(elf.contents(section))==report['functions'][0]['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));runner=decode((ROOT/'build/gx8002-board/kws-run.disassembly.txt').read_text());cases=0
    for index in (0,1,2,3,0xfffffffe,0xffffffff):
      for stride in (0,1,13):
       for seed in (0,91):
        observed=[]
        def acquire(number,context_out,size_out,words):
            record=0x20027be0+(number%3)*8512
            addresses=(record,record+16,context_out,size_out);memory={a+i:0xa5 for a in addresses for i in range(4)}
            result,writes=lookup(code,0x10206ec8,number,context_out,size_out,memory,seed)
            wanted=[(record,0x20027b60),(record+16,record+32),(context_out,record),(size_out,8512)]
            assert result==0 and writes==wanted
            for address,value in writes:words[address]=value
            observed.append(writes)
        args=(0x20030000,index,stride,0x20058000,0x20059000,520,seed)
        actual=execute(runner,0x100260e4,evidence['candidate']['bindings'],*args,context_hook=acquire)
        result,events=expected(*args);previous=0x20027be0+(index%3)*8512;following=0x20027be0+(((index+1)&0xffffffff)%3)*8512
        events=[(e[0],previous+32) if e[0]=='LvpCTCModelGetSnpuFeatsBuffer' else (e[0],following+32) if e[0]=='LvpCTCModelGetSnpuStateBuffer' else (*e[:3],following) if e[0]=='gx_snpu_run_task' else e for e in events]
        assert actual==(result,events) and len(observed)==2;cases+=1
    return {'evidence':evidence,'context_cases':cases,'decoded_context_calls':cases*2,'context_elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Actual decoded ring lookup publishes both contexts into runner local word memory via observed writes; wrap and consecutive same-record selection tested. Other services modeled, physical concurrency and full ring storage lifecycle unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-run-context.json').write_text(json.dumps(r,indent=2)+'\n');print(r['context_cases'])
