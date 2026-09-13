# SPDX-License-Identifier: MIT
"""Independent IEEE binary64 field and normalization oracle."""
import json,subprocess,random
from build_gx8002_unpack_double import build,ROOT
from execute_gx8002_unpack_double import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x13c90','--stop-address=0x13d74',str(p)],text=True));new=decode((ROOT/'build/gx8002-unpack_double/candidate.disassembly.txt').read_text())
    values=[(sign<<63)|(exp<<52)|frac for sign in (0,1) for exp in (0,1,1023,2046,2047) for frac in (0,1,1<<51,(1<<52)-1)]
    values.extend((sign<<63)|(1<<bit) for sign in (0,1) for bit in range(52));rng=random.Random(477);values.extend(rng.getrandbits(64) for _ in range(1000))
    for bits in values:
        source=0x20050000;dest=0x20050100;memory={source+i:b for i,b in enumerate(bits.to_bytes(8,'little'))};memory.update({dest+i:0xa5 for i in range(20)});expected=memory.copy()
        sign=bits>>63;exp=(bits>>52)&2047;frac=bits&((1<<52)-1);word(expected,dest+4,sign)
        if not exp and not frac:word(expected,dest,2)
        elif exp==2047:
            word(expected,dest,(int(bool(frac&(1<<51))) if frac else 4))
            if frac:
                value=(frac&~(1<<51))<<8;word(expected,dest+12,value&0xffffffff);word(expected,dest+16,value>>32)
        else:
            exponent=exp-1023 if exp else frac.bit_length()-1075
            value=((frac|(1<<52))<<8) if exp else frac<<(61-frac.bit_length())
            word(expected,dest,3);word(expected,dest+8,exponent&0xffffffff);word(expected,dest+12,value&0xffffffff);word(expected,dest+16,value>>32)
        def helper(*args):raise ValueError('Unexpected helper')
        for code,entry in ((old,0x13c90),(new,0x1020a704)):
            ret,m,events=execute(code,entry,[source,dest],memory,helper)
            assert ret[0]=='return' and m==expected,(hex(bits),m,expected)
    alias_cases=0
    for bits in values[:144]:
        for displacement in range(-16,9,4):
            source=0x20050020;dest=source+displacement
            memory={i:0xa5 for i in range(source-16,source+32)}
            memory.update({source+i:v for i,v in enumerate(bits.to_bytes(8,'little'))})
            outcomes=[]
            for code,entry in ((old,0x13c90),(new,0x1020a704)):
                ret,m,events=execute(code,entry,[source,dest],memory,helper)
                assert ret[0]=='return';outcomes.append(m)
            assert outcomes[0]==outcomes[1],(hex(bits),displacement)
            alias_cases+=1
    return {'candidate':candidate,'cases':len(values),'alias_cases':alias_cases,'source_admitted':False,'limits':['IEEE field/normalization and preserved unused destination bytes checked; overlapping storage compared. Ordinary memory final state qualified, not concurrent observation of intermediate writes.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-unpack-double-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
