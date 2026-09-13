# SPDX-License-Identifier: MIT
"""PLL wrapper execution with actual decoded counter conversion on raw ticks."""
import json,subprocess
from build_gx8002_clock_pll_wait_candidate import build
from verify_gx8002_clock_time_stock import verify as verify_timer
from verify_gx8002_clock_pll_wait import expected
from execute_gx8002_clock_pll_wait import execute
from verify_gx8002_clock_time_us_candidate import execute as convert
from analyze_gx8002_upstream_objects import ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();timer_evidence=verify_timer();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    stock=decode(subprocess.check_output([pre,'-D','--start-address=0x17020','--stop-address=0x17094',str(p)],text=True))
    new=decode((ROOT/'build/gx8002-board/clock-pll-wait-candidate.disassembly.txt').read_text());timer=decode((ROOT/'build/gx8002-board/clock-time-us-candidate.disassembly.txt').read_text())
    def time_runner(ticks):return convert(timer,ticks&0xffffffff,ticks>>32)
    cases=0
    for start in (0,1,1023,1024,0xffffffff,(1<<64)//1000-1,(1<<64)-2):
        for delta in (0,1,1023,1024,1025,2048,0xffffffff):
            ticks=[start,(start+delta)&((1<<64)-1),(start+delta+1024)&((1<<64)-1)]
            times=[((v*1000)&((1<<64)-1))//1024 for v in ticks]
            for timeout in (0,1,2,4294968,0xffffffff):
                for locks in ([8],[0,8],[0,0,8],[0,0]):
                    a=execute(stock,0x17020,1,timeout,1,locks,ticks,time_runner)
                    b=execute(new,0x1002500c,1,timeout,1,locks,ticks,time_runner)
                    assert a==b==expected(False,1,timeout,locks,times),(start,delta,timeout,locks,a,b)
                    cases+=1
    return {'candidate':candidate,'timer_evidence':timer_evidence,'cases':cases,'source_admitted':False,'limits':['Decoded stock/source wrappers with decoded reconstructed timer; raw hardware counter words scripted and marshalled to timer frame. Counter overflow and timeout boundaries covered. PLL configuration helper remains modeled; hardware timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-pll-wait-timer.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
