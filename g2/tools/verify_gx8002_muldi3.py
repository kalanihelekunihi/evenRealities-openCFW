# SPDX-License-Identifier: MIT
"""Decoded low-64-bit multiplication against arbitrary-precision arithmetic."""
import json,random,subprocess
from itertools import product
from build_gx8002_muldi3 import build,ROOT
from execute_gx8002_muldi3 import execute
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x13ab4','--stop-address=0x13b00',str(path)],text=True));new=decode((ROOT/'build/gx8002-muldi3/candidate.disassembly.txt').read_text())
    edges=(0,1,0xffff,0x10000,0xffffffff,0x100000000,0x7fffffffffffffff,0x8000000000000000,0xffffffffffffffff);values=list(product(edges,edges));rng=random.Random(899);values.extend((rng.getrandbits(64),rng.getrandbits(64)) for _ in range(10000))
    for a,b in values:
        expected=(a*b)&0xffffffffffffffff
        def helper(*args):raise ValueError('Unexpected helper')
        for code,entry in ((old,0x13ab4),(new,0x1020a528)):
            ret,m,events=execute(code,entry,[a&0xffffffff,a>>32,b&0xffffffff,b>>32],{},helper)
            assert ret==('return',expected&0xffffffff,expected>>32) and not m and not events,(hex(a),hex(b),ret,hex(expected))
    return {'candidate':candidate,'cases':len(values),'source_admitted':False,'limits':['Low 64-bit multiplication and target argument/return ABI checked; physical timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-muldi3-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
