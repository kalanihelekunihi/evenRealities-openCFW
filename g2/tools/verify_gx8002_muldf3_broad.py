# SPDX-License-Identifier: MIT
"""Broad decoded multiplication including exceptional binary64 bit patterns."""
import json,subprocess,struct,math,random
from itertools import product
from analyze_gx8002_upstream_objects import ROOT,sha,IMAGE_SHA
from build_transparent_image import Elf32
from execute_gx8002_muldf3 import execute
from verify_gx8002_memcpy_source import decode

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x13694','--stop-address=0x13d74',str(p)],text=True));new={};evidence={}
    for name in ('muldf3','unpack_double','pack_double','muldi3'):
        p=ROOT/('build/gx8002-'+name+'/candidate.elf');e=Elf32(p.read_bytes(),name);r=json.loads((ROOT/('docs/research/gx8002-'+name+'-candidate.json')).read_text());assert sha(e.contents(next(s for s in e.sections if s['name']=='.text')))==r['compiled_sha256'];evidence[name]=sha(p.read_bytes());new.update(decode(subprocess.check_output([pre,'-d',str(p)],text=True)))
    edges=[0,1,0x000fffffffffffff,0x0010000000000000,0x3fefffffffffffff,0x3ff0000000000000,0x3ff0000000000001,0x7fefffffffffffff,0x7ff0000000000000,0x7ff0000000000001,0x7ff8000000001234];edges += [x|(1<<63) for x in edges];values=list(product(edges,edges));rng=random.Random(548);values.extend((rng.getrandbits(64),rng.getrandbits(64)) for _ in range(4000));numeric=0;discrepancies=[]
    for a,b in values:
        results=[execute(code,entry,a,b,up,pk,mul,raw=True) for code,entry,up,pk,mul in ((old,0x13694,0x13c90,0x13b00,0x13ab4),(new,0x1020a108,0x1020a704,0x1020a574,0x1020a528))]
        assert results[0]==results[1],(hex(a),hex(b),results)
        x,y=[struct.unpack('<d',struct.pack('<Q',v))[0] for v in (a,b)];value=x*y
        if not math.isnan(value):
            expected=struct.unpack('<Q',struct.pack('<d',value))[0]
            if results[1]!=expected:discrepancies.append({'left':hex(a),'right':hex(b),'stock_and_source':hex(results[1]),'ieee_expected':hex(expected)})
            numeric+=1
    return {'cases':len(values),'numeric_cases':numeric,'ieee_discrepancies':discrepancies,'elf_sha256':evidence,'limits':['Decoded multiply/unpack/pack/integer helper integration and ABI; exact exceptional payload comparison to stock and explicit discrepancies against non-NaN IEEE host oracle. Physical timing/exception flags unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-muldf3-broad.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
