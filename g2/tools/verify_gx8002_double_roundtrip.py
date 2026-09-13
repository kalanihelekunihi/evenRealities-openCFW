# SPDX-License-Identifier: MIT
"""Decoded source/stock unpack-pack round trips, preserving NaN payload policy."""
import json,random,subprocess
from analyze_gx8002_upstream_objects import ROOT,sha,IMAGE_SHA
from build_transparent_image import Elf32
from execute_gx8002_unpack_double import execute as unpack
from execute_gx8002_pack_double import execute as pack
from verify_gx8002_memcpy_source import decode

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x13b00','--stop-address=0x13d74',str(path)],text=True));codes={};evidence={}
    for name in ('pack_double','unpack_double'):
        path=ROOT/('build/gx8002-'+name+'/candidate.elf');elf=Elf32(path.read_bytes(),name);section=next(s for s in elf.sections if s['name']=='.text');r=json.loads((ROOT/('docs/research/gx8002-'+name+'-candidate.json')).read_text());assert sha(elf.contents(section))==r['compiled_sha256'];evidence[name]=sha(path.read_bytes());codes[name]=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    values=[(sign<<63)|(exp<<52)|frac for sign in (0,1) for exp in (0,1,1023,2046,2047) for frac in (0,1,(1<<51)-1,1<<51,(1<<52)-1)];rng=random.Random(192);values.extend(rng.getrandbits(64) for _ in range(10000))
    for bits in values:
        is_nan=((bits>>52)&2047)==2047 and bool(bits&((1<<52)-1));expected=bits|(1<<51) if is_nan else bits
        for stock in (True,False):
            memory={0x20050000+i:b for i,b in enumerate(bits.to_bytes(8,'little'))};memory.update({0x20050100+i:0xa5 for i in range(20)})
            def helper(*x):raise ValueError('Unexpected helper')
            ret,parts,events=unpack(old if stock else codes['unpack_double'],0x13c90 if stock else 0x1020a704,[0x20050000,0x20050100],memory,helper);assert ret[0]=='return'
            ret,after,events=pack(old if stock else codes['pack_double'],0x13b00 if stock else 0x1020a574,[0x20050100],parts,helper)
            assert ret==('return',expected&0xffffffff,expected>>32) and after==parts and not events,(hex(bits),ret,hex(expected))
    return {'cases':len(values),'elf_sha256':evidence,'limits':['Unpack/pack exact binary64 round trips and upstream NaN quieting policy verified through decoded target code; hardware exception flags and timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-double-roundtrip.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
