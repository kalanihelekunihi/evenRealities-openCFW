# SPDX-License-Identifier: MIT
"""PLL wait stock/source traces against unsigned elapsed-time and lock model."""
import json,subprocess
from build_gx8002_clock_pll_wait_candidate import build
from execute_gx8002_clock_pll_wait import execute
from analyze_gx8002_upstream_objects import ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def expected(blocking,after,timeout,locks,times):
    trace=[('pll',0x20030000),('read',0x20030000,after)]
    if after!=1:return 'return',0,trace
    ti=0
    if not blocking:start=times[ti];ti+=1;trace.append(('time',start))
    for lock in locks:
        trace.append(('read',0xa0005098,lock))
        if lock&8:return 'return',0,trace
        if not blocking:
            now=times[ti];ti+=1;trace.append(('time',now))
            if (now-start)&((1<<64)-1)>(timeout*1000)&MASK:return 'return',MASK,trace
    return 'poll',None,trace

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    stock=decode(subprocess.check_output([pre,'-D','--start-address=0x17020','--stop-address=0x17094',str(p)],text=True))
    source=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/clock-pll-wait-candidate.elf')],text=True));cases=0;polls=0
    for blocking in (False,True):
        for before in (0,1,2,MASK):
            for after in (0,1,2,MASK):
                for timeout in (0,1,4294967,4294968,MASK):
                    limit=(timeout*1000)&MASK
                    for start in (0,0xffffffff,(1<<64)-2):
                        for locks,deltas in (([8],[]),([0,8],[limit]),([0],[limit+1]),([0,0,8],[max(0,limit-1),limit]),([0,0],[0,0])):
                            times=[start]+[(start+x)&((1<<64)-1) for x in deltas]
                            a=execute(stock,0x17074 if blocking else 0x17020,before,timeout,after,locks,times)
                            b=execute(source,0x10025060 if blocking else 0x1002500c,before,timeout,after,locks,times)
                            want=expected(blocking,after,timeout,locks,times)
                            if blocking:
                                a=(a[0],0 if a[0]=='return' else None,a[2]);b=(b[0],0 if b[0]=='return' else None,b[2])
                            assert a==b==want,(blocking,before,after,timeout,start,locks,a,b,want)
                            cases+=1;polls+=int(a[0]=='poll')
    return {'candidate':candidate,'cases':cases,'continuing_poll_cases':polls,'source_admitted':False,'limits':['Complete decoded wrapper traces and integer ABI on returns. Poll outcomes stop at a scripted MMIO boundary, not proof of eventual return. PLL/time helpers modeled; hardware lock timing and decoded helper integration remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-pll-wait.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
