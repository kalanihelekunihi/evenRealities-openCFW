# SPDX-License-Identifier: MIT
import json,random,subprocess
from oracle_gx8002_timer_dispatch import expected
from build_gx8002_timer_dispatch_candidate import build,ROOT
from execute_gx8002_timer_dispatch import execute,BASE
from analyze_gx8002_upstream_objects import sha,IMAGE_SHA
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def verify(nested_timer=False):
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x178d8','--stop-address=0x17944',str(p)],text=True));new=decode((ROOT/'build/gx8002-board/timer-dispatch-candidate.disassembly.txt').read_text());rng=random.Random(1024);cases=0
    timer_evidence={};runner=None
    if nested_timer:
        from verify_gx8002_clock_time_us_candidate import execute as timer_execute
        p=ROOT/'build/gx8002-board/clock-time-us-candidate.elf';elf=Elf32(p.read_bytes(),'timer')
        reviewed=json.loads((ROOT/'docs/research/gx8002-clock-time-us-source-verification.json').read_text());row=reviewed['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
        timer_code=decode(subprocess.check_output([pre,'-d',str(p)],text=True));timer_evidence={'elf_sha256':sha(p.read_bytes())}
        runner=lambda ticks:timer_execute(timer_code,ticks&0xffffffff,ticks>>32)
    for index in range(512):
        memory={0xa0400000:rng.getrandbits(32)};times=[]
        for slot in range(10):
            a=BASE+36*slot;ticks=rng.getrandbits(64);now=((ticks*1000)&((1<<64)-1))//1024 if nested_timer else ticks;due=(now+(-1,0,1)[(index+slot)%3])&((1<<64)-1);active=(index>> (slot%9))&1
            values=[0x10001000+4*slot,slot,rng.getrandbits(32),0,0,due&0xffffffff,due>>32,active,index%2]
            memory.update({a+4*i:v for i,v in enumerate(values)})
            if active:times.append(ticks if nested_timer else now)
        def callback(target,arg,m):
            assert target==0x10001000+4*arg;addr=BASE+36*arg
            if index%3==0:m[addr+8]=(0,1,2147484,0xffffffff)[arg%4];m[addr+32]=arg%2
            if index%5==0:m[addr+28]=0
        a=execute(old,0x178d8,memory,times,callback,runner);b=execute(new,0x100258c4,memory,times,callback,runner);want_times=[((v*1000)&((1<<64)-1))//1024 for v in times] if nested_timer else times;assert a==b==expected(memory,want_times,callback),index;cases+=1
    return {'candidate':candidate,'cases':cases,'timer_evidence':timer_evidence,'source_admitted':False,'limits':['Decoded stock/source ordered state and callback traces, callback mutation and integer ABI. Time/callback boundaries modeled. Independent scheduling model checked. State ownership, hardware timing and placement remain outstanding.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-timer-dispatch-paths.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
