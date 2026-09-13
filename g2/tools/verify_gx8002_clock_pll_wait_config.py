# SPDX-License-Identifier: MIT
"""Decoded PLL programming followed by recovered blocking/timed lock polling."""
import json,random,subprocess
from build_gx8002_clock_pll_wait_candidate import build
from execute_gx8002_clock_pll_wait import execute
from verify_gx8002_clock_pll_wait import expected
from verify_gx8002_clock_pll import execute as configure,oracle,OFFSETS
from verify_gx8002_clock_time_us_candidate import execute as convert
from analyze_gx8002_upstream_objects import ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    stock=decode(subprocess.check_output([pre,'-D','--start-address=0x17020','--stop-address=0x17094',str(p)],text=True));new=decode((ROOT/'build/gx8002-board/clock-pll-wait-candidate.disassembly.txt').read_text())
    codes={};hashes={}
    for name,report_name in (('clock-pll','gx8002-clock-pll-source-verification.json'),('clock-time-us','gx8002-clock-time-us-source-verification.json')):
        p=ROOT/f'build/gx8002-board/{name}-candidate.elf';e=Elf32(p.read_bytes(),name);report=json.loads((ROOT/'docs/research'/report_name).read_text());row=report['functions'][0];section=next(s for s in e.sections if s['name']==row['section_name']);assert sha(e.contents(section))==row['compiled_sha256']
        codes[name]=decode(subprocess.check_output([pre,'-d',str(p)],text=True));hashes[name]=sha(p.read_bytes())
    rng=random.Random(912);cases=0
    for blocking in (False,True):
        for enable in (0,1,2,0xffffffff):
            for index in range(64):
                fields=[rng.getrandbits(32) for _ in range(14)];fields[0]=enable;registers={o:rng.getrandbits(32) for o in OFFSETS};perturb=index%3
                want_config=oracle(True,fields,registers,perturb)
                def pll_runner(actual_enable):
                    assert actual_enable==enable
                    result=configure(codes['clock-pll'],0x10024b04,True,fields,registers,perturb);assert result==want_config
                    return result[0]
                def timer(ticks):return convert(codes['clock-time-us'],ticks&0xffffffff,ticks>>32)
                ticks=[index*1024,index*1024+1024,index*1024+2048];times=[((v*1000)&((1<<64)-1))//1024 for v in ticks]
                locks=([8],[0,8],[0,0,8],[0,0])[index%4];timeout=index%3
                a=execute(stock,0x17074 if blocking else 0x17020,enable,timeout,enable,locks,ticks,timer,pll_runner)
                b=execute(new,0x10025060 if blocking else 0x1002500c,enable,timeout,enable,locks,ticks,timer,pll_runner)
                want=expected(blocking,enable,timeout,locks,times);want=(want[0],want[1],want[2][:1]+want_config[0]+want[2][1:])
                if blocking:a=(a[0],0 if a[0]=='return' else None,a[2]);b=(b[0],0 if b[0]=='return' else None,b[2])
                assert a==b==want,(blocking,enable,index,a,b,want);cases+=1
    return {'candidate':candidate,'cases':cases,'dependency_elf_sha256':hashes,'source_admitted':False,'limits':['Decoded configuration/timer helpers with private parameter/MMIO snapshot marshalling, ordered configuration then polling checked against independent models. Hardware lock feedback and timing remain scripted, not physically qualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-pll-wait-config.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
