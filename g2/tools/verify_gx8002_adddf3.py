# SPDX-License-Identifier: MIT
"""Addition wrapper parts/sign and returned-pointer routing oracle."""
import json,subprocess
from itertools import product
from build_gx8002_adddf3 import build,ROOT
from execute_gx8002_subdf3 import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x13628','--stop-address=0x13658',str(p)],text=True));new=decode((ROOT/'build/gx8002-adddf3/candidate.disassembly.txt').read_text());cases=0
    for sa,sb,target,result in product((0,1),(0,1),(0,1,2),((0,0),(0xffffffff,0x7ff80000),(0x12345678,0xabcdef01))):
        for code,entry in ((old,0x13628),(new,0x1020a09c)):
            parts=[];seen=[];arguments=[1,2,3,4]
            def helper(t,a,m,e):
                if t==0x1020a704:
                    index=len(parts);seen.append(('unpack',word(m,a[0]),word(m,a[0]+4)));parts.append(a[1])
                    for i,v in enumerate((3,sa if index==0 else sb,0,0,0x10000000)):word(m,a[1]+4*i,v)
                    return 0xffffffff
                if t==0x10209dd8:
                    assert a[:2]==parts and word(m,a[0]+4)==sa and word(m,a[1]+4)==sb
                    seen.append(('add',));parts.append(a[2]);return parts[target]
                assert t==0x1020a574 and a[0]==parts[target];seen.append(('pack',target));return result
            ret,m,events=execute(code,entry,arguments,{},helper)
            assert ret==('return',*result) and not m and seen==[('unpack',1,2),('unpack',3,4),('add',),('pack',target)]
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Unpack order, operand sign preservation, arithmetic result pointer and double return ABI checked; addition core arithmetic remains separate.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-adddf3-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
