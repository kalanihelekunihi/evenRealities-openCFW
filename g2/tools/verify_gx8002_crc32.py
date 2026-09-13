# SPDX-License-Identifier: MIT
"""Compare decoded CRC core against an independent bitwise polynomial oracle."""
import json,subprocess,zlib
from itertools import product
from build_gx8002_crc32 import build,ROOT,IMAGE,Elf32
from execute_gx8002_crc32 import execute
from verify_gx8002_memcpy_source import decode

def verify():
    report=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12d80','--stop-address=0x12e40',str(p)],text=True))
    new=decode((ROOT/'build/gx8002-crc32/candidate.disassembly.txt').read_text())
    elf=Elf32((ROOT/'build/gx8002-crc32/candidate.elf').read_bytes(),'candidate');table=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.crc_table'))
    def step(crc):
        for _ in range(8):crc=(crc>>1)^(0xedb88320 if crc&1 else 0)
        return crc
    assert table==b''.join(step(i).to_bytes(4,'little') for i in range(256))
    cases=0
    for alignment,length,seed in product(range(4),range(65),(0,1,0x80000000,0xffffffff)):
        data=bytes((i*73+length*11)&255 for i in range(length));expected=seed
        for byte in data:expected=step(expected^byte)
        address=0x20050000+alignment;memory={address+i:v for i,v in enumerate(data)};memory.update({0x1020b908+i:v for i,v in enumerate(table)})
        def helper(*args):raise ValueError('Unexpected helper')
        for code,entry in ((old,0x12d80),(new,0x102097f4)):
            ret,m,events=execute(code,entry,[seed,address,length],memory,helper)
            assert ret==('return',expected) and m==memory and not events,(alignment,length,seed,ret,expected)
        for code,entry,core in ((old,0x12e34,0x12d80),(new,0x102098a8,0x102097f4)):
            def nested(target,args,m,e):
                assert target==0x102097f4
                result,after,events=execute(code,core,args[:3],m,helper)
                assert result[0]=='return' and after==m and not events
                return result[1]
            ret,m,events=execute(code,entry,[seed,address,length],memory,nested)
            assert ret==('return',zlib.crc32(data,seed)&0xffffffff) and m==memory and not events
        cases+=1
    return {'candidate':report,'cases':cases,'source_admitted':False,'limits':['Decoded stock/source core and nested wrapper checked against bitwise polynomial and zlib oracles; hardware timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-crc32-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
