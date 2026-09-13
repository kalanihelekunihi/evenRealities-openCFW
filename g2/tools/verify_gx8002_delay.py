# SPDX-License-Identifier: MIT
import json,subprocess
from build_gx8002_delay_candidate import build,ROOT
from execute_gx8002_delay import execute
from analyze_gx8002_upstream_objects import sha,IMAGE_SHA
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def expected(usec,times):
    now=times[0];deadline=(now+usec+1)&((1<<64)-1);trace=[('time',now)];i=1
    while now<deadline:
        trace.append(('backoff',50))
        if i==len(times):return 'poll',trace
        now=times[i];i+=1;trace.append(('time',now))
    return 'return',trace

def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x17958','--stop-address=0x179a0',str(p)],text=True));new=decode((ROOT/'build/gx8002-board/delay-candidate.disassembly.txt').read_text());cases=0
    for start in (0,1,0xffffffff,1<<32,(1<<64)-2,(1<<64)-1):
        for usec in (0,1,999,1000,0x7fffffff,0xffffffff):
            due=(start+usec+1)&((1<<64)-1)
            for times in ([start],[start,start],[start,due],[start,(due-1)&((1<<64)-1),due],[start,(due+1)&((1<<64)-1)]):
                a=execute(old,0x17958,usec,times);b=execute(new,0x10025944,usec,times);assert a==b==expected(usec,times),(start,usec,times,a,b);cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Decoded microsecond stock/source, independent deadline/backoff oracle and integer ABI. Time helper modeled; millisecond wrapper and decoded timer integration remain outstanding. Physical delay timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-delay.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
