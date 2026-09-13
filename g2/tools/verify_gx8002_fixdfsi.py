# SPDX-License-Identifier: MIT
"""Nested signed conversion oracle including saturation and NaN behavior."""
import json,struct,math,random,subprocess
from build_gx8002_fixdfsi import build,ROOT
from build_gx8002_unpack_double import build as build_unpack
from execute_gx8002_fixdfsi import execute
from execute_gx8002_unpack_double import execute as unpack
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();unpacker=build_unpack();p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x139ec','--stop-address=0x13d74',str(p)],text=True));new=decode((ROOT/'build/gx8002-fixdfsi/candidate.disassembly.txt').read_text());ucode=decode((ROOT/'build/gx8002-unpack_double/candidate.disassembly.txt').read_text())
    values=[0.,-0.,0.5,-0.5,1.9,-1.9,2147483647.,2147483648.,-2147483648.,-2147483649.,float('inf'),float('-inf'),float('nan')];bits=[struct.unpack('<Q',struct.pack('<d',v))[0] for v in values];rng=random.Random(833);bits.extend(rng.getrandbits(64) for _ in range(1000))
    for raw in bits:
        v=struct.unpack('<d',struct.pack('<Q',raw))[0];expected=0 if math.isnan(v) else 2147483647 if v>=2147483647 else -2147483648 if v<=-2147483648 else int(v)
        for stock in (True,False):
            def helper(t,a,m,e):
                assert t==0x1020a704
                ret,after,events=unpack(old if stock else ucode,0x13c90 if stock else t,a[:2],m,lambda *x:None)
                assert ret[0]=='return';m.clear();m.update(after);return 0
            ret,m,events=execute(old if stock else new,0x139ec if stock else 0x1020a460,[raw&0xffffffff,raw>>32],{},helper)
            assert ret==('return',expected&0xffffffff) and not m,(hex(raw),ret,expected)
    return {'candidate':candidate,'unpacker':unpacker,'cases':len(bits),'source_admitted':False,'limits':['Nested decoded unpack and signed conversion checked; physical exception flags and timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-fixdfsi-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
