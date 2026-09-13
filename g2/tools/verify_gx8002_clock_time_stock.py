# SPDX-License-Identifier: MIT
"""Decoded stock timer plus actual decoded division versus reconstructed source."""
import json,subprocess,random
from verify_gx8002_clock_time_us_candidate import execute as source,build,ROOT,decode
from execute_gx8002_clock_time_stock import execute as stock
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32

def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    def code(lo,hi):return decode(subprocess.check_output([pre,'-D',f'--start-address={lo:#x}',f'--stop-address={hi:#x}',str(p)],text=True))
    timer=code(0x17870,0x178d8);divider=code(0x12e40,0x12ee8);new=decode((ROOT/'build/gx8002-board/clock-time-us-candidate.disassembly.txt').read_text())
    rng=random.Random(909);values=[0,1,1023,1024,4294967,4294968,0xffffffff,1<<32,(1<<64)//1000-1,(1<<64)//1000,(1<<64)//1000+1,(1<<64)-1]+[rng.getrandbits(64) for _ in range(2048)]
    for ticks in values:
        lo=ticks&0xffffffff;hi=ticks>>32;want=((ticks*1000)&((1<<64)-1))//1024
        assert stock(timer,lo,hi,divider)==source(new,lo,hi)==want,ticks
    return {'candidate':candidate,'cases':len(values),'source_admitted':False,'limits':['Decoded stock timer and stock div64 fallback, source timer, read order and integer ABI match independent arithmetic. Division stack buffer marshalled across helper frames. Wrapper integration and hardware snapshot timing remain outstanding.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-time-stock.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
