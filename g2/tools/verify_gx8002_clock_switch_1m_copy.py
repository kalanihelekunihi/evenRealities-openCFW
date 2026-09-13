# SPDX-License-Identifier: MIT
"""Source selector initializer copied by authenticated decoded memcpy."""
import json,struct,subprocess
from verify_gx8002_clock_switch_1m import verify as qualify,execute,expected
from verify_gx8002_memcpy_source import execute as copy,decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha


def verify():
    evidence=qualify();path=ROOT/'build/gx8002-memcpy-source/copy.o';elf=Elf32(path.read_bytes(),'copy');report=json.loads((ROOT/'build/gx8002-memcpy-source/verification.json').read_text());section=next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_memcpy');assert sha(elf.contents(section))==report['compiled_sha256']
    p=ROOT/'build/gx8002-board/clock-switch-1m-candidate.elf';outer_elf=Elf32(p.read_bytes(),'outer');data=outer_elf.contents(next(s for s in outer_elf.sections if s['name']=='.rodata'));assert sha(data)==evidence['candidate']['source_data']['sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-dr',str(path)],text=True));outer=decode((ROOT/'build/gx8002-board/clock-switch-1m-candidate.disassembly.txt').read_text());cases=0;calls=0
    for fill in (0,0xff,0xa5,0x5a):
        for enable in (0,1,2,0xffffffff):
            def transfer(dst,src,count):
                nonlocal calls
                assert count==16 and src==0x10025cd0
                memory={src+i:v for i,v in enumerate(data)};memory.update({dst+i:fill for i in range(-4,20)});before=dict(memory);accesses=[]
                ret,trace=copy(code,memory,dst,src,count,accesses=accesses)
                assert ret==dst and bytes(memory[dst+i] for i in range(16))==data
                assert all(memory[a]==v for a,v in before.items() if not dst<=a<dst+16)
                assert sorted(a for kind,a in trace if kind=='read')==list(range(src,src+16))
                assert sorted(a for kind,a in trace if kind=='write')==list(range(dst,dst+16));calls+=1
                return struct.unpack('<4I',bytes(memory[dst+i] for i in range(16)))
            answers={m:m&1 for m in range(11,26)}
            assert execute(outer,0x10025a14,answers,0,enable,(28,0,18,1),copy_runner=transfer)==expected(answers,0,enable);cases+=1
    return {'evidence':evidence,'cases':cases,'decoded_copy_calls':calls,'copy_object_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Actual compiled selector data copied with decoded source memcpy; source preservation, destination bounds and exact byte access coverage checked. Private destination frame marshalled back to outer executor. Other helpers modeled here; hardware timing unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-switch-1m-copy.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
