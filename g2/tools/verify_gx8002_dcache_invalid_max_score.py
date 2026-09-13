# SPDX-License-Identifier: MIT
"""Compose the admitted MAX scorer with reconstructed cache invalidation."""
import json,subprocess
from verify_gx8002_dcache_invalid_range import verify as qualify,execute as invalidate,expected,ADDRESS,ROOT
from verify_gx8002_max_score import BASE,CTX,HEADER,PARAM,OUTPUT
from execute_gx8002_max_score import execute
from verify_gx8002_power_initialize import word
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-max-score/candidate.elf'
    report_path=ROOT/'docs/research/gx8002-max-score-source-verification.json'
    report=json.loads(report_path.read_text());elf=Elf32(path.read_bytes(),'max')
    for row in report.get('functions',[report]):
        sec=next(s for s in elf.sections if s['name']==row['section_name'])
        assert sha(elf.contents(sec))==row['compiled_sha256'] and not elf.relocations(sec['index'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    caller=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    callee=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/dcache-invalid-range-candidate.elf')],text=True))
    cases=0
    for pointer in (OUTPUT,OUTPUT+1,OUTPUT+15,0xfffffff1):
      for size in (0,1,15,16,17,127,128,129,257,0x80000000,0xffffffff):
        memory={a+i:0 for a,n in ((BASE-16,132),(CTX,32),(HEADER,80)) for i in range(n)}
        word(memory,BASE+88,0);word(memory,CTX,HEADER);word(memory,CTX+16,pointer);word(memory,HEADER+68,size)
        memory[BASE]=0x5a;memory[BASE+1]=0xa5;memory[CTX+13]=0x7f
        wanted_memory=memory.copy();wanted_memory[BASE]=wanted_memory[BASE+1]=wanted_memory[CTX+13]=0
        calls=[]
        def helper(target,args,f,sp,state,events):
            a,b,c,d=args
            if target==0x102099cc:
                assert (a,b,c)==(BASE,0,2)
                for i in range(c):state[a+i]=b
                return a,None
            if target==ADDRESS:
                assert (a,b)==(pointer,size)
                observed,done=invalidate(callee,ADDRESS,a,b,0xffffffff)
                assert done and observed==expected(pointer,size)
                calls.append(observed);return 0,None
            if target==0x10208c60:return pointer,None
            raise ValueError(('unexpected helper',hex(target)))
        result=execute(caller,0x102086dc,CTX,0,memory,helper)
        assert result[0]==('return',0) and result[1]==wanted_memory and len(calls)==1
        cases+=1
    return {'evidence':evidence,'caller_elf_sha256':sha(path.read_bytes()),'caller_report_sha256':sha(report_path.read_bytes()),'composed_cases':cases,'source_admitted':False,'limits':['Decoded scorer invalidation call and complete cache traces tested with zero configured scores. Scoring arithmetic covered separately; no physical cache coherence qualification. Huge positive lengths retain the separate prefix-only limitation.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-dcache-invalid-max-score.json').write_text(json.dumps(r,indent=2)+'\n');print(r['composed_cases'])
