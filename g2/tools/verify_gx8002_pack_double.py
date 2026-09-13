# SPDX-License-Identifier: MIT
"""Decoded binary64 packing against integer rounding oracle."""
import json,subprocess,random,struct
from build_gx8002_pack_double import build,ROOT
from verify_gx8002_pack_double_host import oracle
from execute_gx8002_pack_double import execute
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x13b00','--stop-address=0x13c90',str(p)],text=True));new=decode((ROOT/'build/gx8002-pack_double/candidate.disassembly.txt').read_text())
    values=[(c,s,e,f) for c in range(5) for s in (0,1) for e in (-1100,-1075,-1074,-1023,-1022,0,1023,1024) for f in (1<<60,(1<<60)+128,(1<<60)+384,(1<<61)-1)]
    rng=random.Random(738);values.extend((3,rng.randrange(2),rng.randrange(-1100,1025),rng.randrange(1<<60,1<<61)) for _ in range(2000))
    values.extend((3,s,-1022-shift,(1<<60)|tail) for shift in range(1,57) for s in (0,1) for tail in (0,1,(1<<shift)-1,1<<shift))
    values.extend((3,s,e,base+guard) for s in (0,1) for e in (-1023,-1022,0,1023) for base in (1<<60,(1<<60)+256,(1<<61)-512) for guard in range(512))
    for c,s,e,f in values:
        address=0x20050000;memory={address+i:v for i,v in enumerate(struct.pack('<IIiQ',c,s,e,f))};expected=oracle(c,s,e,f)
        def helper(*args):raise ValueError('Unexpected helper')
        for code,entry in ((old,0x13b00),(new,0x1020a574)):
            ret,m,events=execute(code,entry,[address],memory,helper)
            assert ret==('return',expected&0xffffffff,expected>>32) and m==memory and not events,(c,s,e,hex(f),ret,hex(expected))
    return {'candidate':candidate,'cases':len(values),'source_admitted':False,'limits':['Decoded stock/source integer rounding and ABI checked; physical floating exception flags and timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-pack-double-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
