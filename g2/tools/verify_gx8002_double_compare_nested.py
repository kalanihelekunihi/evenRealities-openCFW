# SPDX-License-Identifier: MIT
"""Execute recovered comparison wrapper, unpacker and parts core together."""
import json,struct,math,subprocess
from itertools import product
from build_gx8002_gedf2 import build as build_wrapper,ROOT
from build_gx8002_unpack_double import build as build_unpack
from build_gx8002_fpcmp_parts import build as build_compare
from execute_gx8002_gedf2 import execute as wrapper
from execute_gx8002_unpack_double import execute as unpack
from execute_gx8002_fpcmp_parts import execute as compare
from verify_gx8002_memcpy_source import decode

def verify():
    builds=[build_wrapper(),build_unpack(),build_compare()]
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x139ac','--stop-address=0x13e36',str(p)],text=True))
    codes=[decode((ROOT/('build/gx8002-'+name+'/candidate.disassembly.txt')).read_text()) for name in ('gedf2','unpack_double','fpcmp_parts')]
    bits=[0,1,0x000fffffffffffff,0x0010000000000000,0x3fefffffffffffff,0x3ff0000000000000,0x41e0000000000000,0x7fefffffffffffff,0x7ff0000000000000,0x7ff0000000000001,0x7ff8000000000001]
    bits+= [b|(1<<63) for b in bits];cases=0
    def numeric(b):return struct.unpack('<d',struct.pack('<Q',b))[0]
    for a,b in product(bits,bits):
        fa,fb=numeric(a),numeric(b);expected=-1 if math.isnan(fa) or math.isnan(fb) else (fa>fb)-(fa<fb)
        for stock in (True,False):
            def helper(t,args,m,e):
                if t==0x1020a704:run=unpack;code=old if stock else codes[1];entry=0x13c90 if stock else t
                elif t==0x1020a7e8:run=compare;code=old if stock else codes[2];entry=0x13d74 if stock else t
                else:raise ValueError('Unexpected helper')
                ret,after,events=run(code,entry,args[:2],m,lambda *x:(_ for _ in ()).throw(ValueError('Unexpected nested call')))
                assert ret[0]=='return';m.clear();m.update(after);return ret[1]
            ret,m,events=wrapper(old if stock else codes[0],0x139ac if stock else 0x1020a420,[a&0xffffffff,a>>32,b&0xffffffff,b>>32],{},helper)
            assert ret==('return',expected&0xffffffff) and not m,(hex(a),hex(b),ret,expected)
        cases+=1
    return {'builds':builds,'cases':cases,'limits':['Decoded nested comparison path checked against binary64 ordering including NaNs/subnormals; physical timing and exception flags unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-double-compare-nested.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
