# SPDX-License-Identifier: MIT
"""Unpack/classification/parts-comparison wrapper boundary oracle."""
import json,subprocess
from itertools import product
from build_gx8002_gedf2 import build,ROOT
from execute_gx8002_gedf2 import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x139ac','--stop-address=0x139ec',str(path)],text=True));new=decode((ROOT/'build/gx8002-gedf2/candidate.disassembly.txt').read_text());cases=0
    for ca,cb,result in product((0,1,2,3,4,0xffffffff),(0,1,2,3,4,0xffffffff),(0,1,0xffffffff,0x80000000)):
        arguments=[0x12345678,0x7ff80000,0x87654321,0xbff00000]
        expected=[('unpack',*arguments[:2]),('unpack',*arguments[2:])]
        if ca not in (0,1) and cb not in (0,1):expected.append(('compare',ca,cb))
        for code,entry in ((old,0x139ac),(new,0x1020a420)):
            calls=[];parts=[]
            def helper(t,a,m,e):
                if t==0x1020a704:
                    pair=(word(m,a[0]),word(m,a[0]+4));e.append(('unpack',*pair));classification=ca if not calls else cb;calls.append(pair);parts.append(a[1])
                    for offset in range(0,20,4):word(m,a[1]+offset,classification if not offset else offset)
                    return 0xffffffff
                assert t==0x1020a7e8 and a[:2]==parts
                e.append(('compare',word(m,a[0]),word(m,a[1])));return result
            ret,m,events=execute(code,entry,arguments,{},helper)
            assert ret==('return',0xffffffff if ca in (0,1) or cb in (0,1) else result) and not m and events==expected,(ca,cb,ret,events,expected)
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Classification and helper-boundary oracle checks unpack order, frame layout, return preservation and ABI; nested floating semantics remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-gedf2-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
