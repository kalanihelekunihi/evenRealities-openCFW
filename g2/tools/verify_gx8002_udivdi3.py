# SPDX-License-Identifier: MIT
"""Decoded unsigned division against stock and arbitrary precision quotient."""
import json,random,subprocess
from itertools import product
from build_gx8002_udivdi3 import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_udivdi3 import execute

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(stock.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x13030','--stop-address=0x13364',str(stock)],text=True))
    new=decode((ROOT/'build/gx8002-udivdi3/candidate.disassembly.txt').read_text())
    # Stock lookup semantics independently generated, then authenticated byte-exact.
    table=bytes(i.bit_length() for i in range(256))
    ce=Elf32((ROOT/'build/gx8002-udivdi3/candidate.elf').read_bytes(),'candidate')
    assert ce.contents(next(s for s in ce.sections if s['name']=='.rodata.clz'))==table
    assert table==IMAGE.read_bytes()[0x152a8:0x153a8]
    edges=[0,1,2,3,0xffff,0x10000,0xffffffff,0x100000000,0x7fffffffffffffff,0x8000000000000000,0xffffffffffffffff]
    values=list(product(edges,edges[1:]));rng=random.Random(764)
    values.extend((rng.getrandbits(64),rng.getrandbits(64) or 1) for _ in range(3000))
    values.extend((rng.getrandbits(64),1<<i) for i in range(64))
    values.extend((rng.getrandbits(64),rng.getrandbits(32) or 1) for _ in range(1000))
    for a,b in values:
        for code,entry in ((old,0x13030),(new,0x10209aa4)):
            got=execute(code,entry,a,b,raw=True)
            assert got==a//b,(hex(a),hex(b),hex(got),hex(a//b))
    for a in edges:
        for code,entry in ((old,0x13030),(new,0x10209aa4)):
            try:execute(code,entry,a,0,raw=True)
            except ZeroDivisionError:pass
            else:raise AssertionError('Missing divide exception')
    return {'candidate':candidate,'cases':len(values),'zero_divisor_cases':len(edges),'lookup_sha256':sha(table),'limits':['Decoded integer ABI, quotient and divide-by-zero behavior only; execution timing and hardware exception delivery unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-udivdi3-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
