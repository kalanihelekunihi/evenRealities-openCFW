# SPDX-License-Identifier: MIT
"""Decoded subtraction, unpacking, parts addition and packing integration."""
import json,subprocess,struct,math,random
from itertools import product
from analyze_gx8002_upstream_objects import ROOT,sha,IMAGE_SHA
from build_transparent_image import Elf32
from execute_gx8002_subdf3 import execute as wrapper
from execute_gx8002_unpack_double import execute as unpack
from execute_gx8002_fpadd_parts import execute as add
from execute_gx8002_pack_double import execute as pack
from verify_gx8002_power_initialize import word
from verify_gx8002_memcpy_source import decode

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x13364','--stop-address=0x13d74',str(path)],text=True));codes={};evidence={}
    for name in ('subdf3','unpack_double','fpadd_parts','pack_double'):
        path=ROOT/('build/gx8002-'+name+'/candidate.elf');elf=Elf32(path.read_bytes(),name);r=json.loads((ROOT/('docs/research/gx8002-'+name+'-candidate.json')).read_text());assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.text')))==r['compiled_sha256'];evidence[name]=sha(path.read_bytes());codes[name]=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    edges=[0,1,0x000fffffffffffff,0x0010000000000000,0x3ff0000000000000,0x7fefffffffffffff,0x7ff0000000000000,0x7ff0000000000001,0x7ff8000000000123];edges += [v|(1<<63) for v in edges]
    values=list(product(edges,edges));rng=random.Random(118);values.extend((rng.getrandbits(64),rng.getrandbits(64)) for _ in range(3000));finite=0
    for left,right in values:
        outcomes=[]
        for stock in (True,False):
            memory={0x1020bd08+i:0 for i in range(20)}
            def helper(t,a,m,e):
                if t==0x1020a704:
                    ret,after,events=unpack(old if stock else codes['unpack_double'],0x13c90 if stock else t,a[:2],m,helper);assert ret[0]=='return';m.clear();m.update(after);return 0
                if t==0x10209dd8:
                    # The word-memory core executor uses fixed addresses. Map
                    # caller fields and returned pointer without mocking arithmetic.
                    fields=[{off:word(m,p+off) for off in (0,4,8,12,16)} for p in a[:2]]
                    pointer,after=add(old if stock else codes['fpadd_parts'],0x13364 if stock else t,*fields,full=True)
                    mapping={0x20040000:a[0],0x20040100:a[1],0x20040200:a[2],0x1020bd08:0x1020bd08}
                    for fixed,actual in mapping.items():
                        for off in (0,4,8,12,16):word(m,actual+off,after[fixed+off])
                    return mapping[pointer]
                assert t==0x1020a574
                ret,after,events=pack(old if stock else codes['pack_double'],0x13b00 if stock else t,a[:1],m,helper);assert after==m and not events;return ret[1:]
            ret,m,events=wrapper(old if stock else codes['subdf3'],0x13658 if stock else 0x1020a0cc,[left&0xffffffff,left>>32,right&0xffffffff,right>>32],memory,helper)
            assert ret[0]=='return' and m==memory;outcomes.append(ret[1]|(ret[2]<<32))
        assert outcomes[0]==outcomes[1],(hex(left),hex(right),outcomes)
        x,y=[struct.unpack('<d',struct.pack('<Q',v))[0] for v in (left,right)]
        if not math.isnan(x-y):
            expected=struct.unpack('<Q',struct.pack('<d',x-y))[0];assert outcomes[1]==expected,(hex(left),hex(right),outcomes,hex(expected));finite+=1
    return {'cases':len(values),'numeric_oracle_cases':finite,'elf_sha256':evidence,'limits':['All four decoded routines execute; parts-core fixed-memory addresses are explicitly marshalled at the call boundary. Exact stock/source bits and non-NaN host IEEE results checked; timing and physical exception flags unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-subdf3-nested.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
