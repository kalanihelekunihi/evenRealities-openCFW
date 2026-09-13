# SPDX-License-Identifier: MIT
"""Decoded 64/32 quotient, remainder and memory mutation oracle."""
import json,subprocess,random
from build_gx8002_div64 import build,ROOT
from execute_gx8002_div64 import execute
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12e40','--stop-address=0x12ee8',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-div64/candidate.disassembly.txt').read_text())
    values=[(n,d) for n in (0,1,0xffffffff,0x100000000,0x7fffffffffffffff,0x8000000000000000,0xffffffffffffffff) for d in (1,2,3,0x7fffffff,0x80000000,0xffffffff)]
    rng=random.Random(123);values.extend((rng.getrandbits(64),rng.randrange(1,1<<32)) for _ in range(1000))
    for n,d in values:
        address=0x20050000;memory={address+i:b for i,b in enumerate(n.to_bytes(8,'little'))};q,rem=divmod(n,d);expected={address+i:b for i,b in enumerate(q.to_bytes(8,'little'))}
        def helper(*args):raise ValueError('Unexpected helper')
        for code,entry in ((old,0x12e40),(new,0x102098b4)):
            ret,m,events=execute(code,entry,[address,d],memory,helper)
            assert ret==('return',rem) and m==expected,(n,d,ret,rem,m,expected)
    zero_cases=0
    for n in (0,1,0xffffffff,0x100000000,0xffffffffffffffff):
        address=0x20050000;memory={address+i:b for i,b in enumerate(n.to_bytes(8,'little'))}
        for code,entry in ((old,0x12e40),(new,0x102098b4)):
            ret,m,events=execute(code,entry,[address,0],memory,helper)
            assert ret==('divide_exception',) and m==memory and not events
        zero_cases+=1
    return {'zero_divisor_cases':zero_cases,'candidate':candidate,'cases':len(values),'source_admitted':False,'limits':['Positive divisors checked against Python arbitrary-precision divmod, complete memory and integer ABI; zero divisors reach decoded divide exception without writes; hardware exception delivery and timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-div64-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
