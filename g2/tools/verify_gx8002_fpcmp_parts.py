# SPDX-License-Identifier: MIT
"""Independent sign/magnitude ordering oracle for floating-point parts."""
import json,subprocess,struct
from itertools import product
from build_gx8002_fpcmp_parts import build,ROOT
from execute_gx8002_fpcmp_parts import execute
from verify_gx8002_memcpy_source import decode

def oracle(a,b):
    ca,sa,ea,fa=a;cb,sb,eb,fb=b
    if ca<2 or cb<2:return 1
    if ca==2 and cb==2:return 0
    def key(c,s,e,f):
        if c==2:return (0,0,0,0)
        sign=-1 if s else 1
        return (sign,sign*(2 if c==4 else 1),sign*e if c!=4 else 0,sign*f if c!=4 else 0)
    ka=key(*a);kb=key(*b);return (ka>kb)-(ka<kb)
def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x13d74','--stop-address=0x13e36',str(p)],text=True));new=decode((ROOT/'build/gx8002-fpcmp_parts/candidate.disassembly.txt').read_text());cases=0
    for ca,cb,sa,sb,ea,eb,fa,fb in product(range(5),range(5),range(2),range(2),(-1074,0,1023),(-1074,0,1023),(1<<60,(1<<61)-1),(1<<60,(1<<60)+1)):
        a=(ca,sa,ea,fa);b=(cb,sb,eb,fb);memory={}
        for address,parts in ((0x20050000,a),(0x20050100,b)):
            memory.update({address+i:v for i,v in enumerate(struct.pack('<IIiQ',*parts))})
        def helper(*args):raise ValueError('Unexpected helper')
        for code,entry in ((old,0x13d74),(new,0x1020a7e8)):
            ret,m,events=execute(code,entry,[0x20050000,0x20050100],memory,helper)
            assert ret==('return',oracle(a,b)&0xffffffff) and m==memory and not events,(a,b,ret,oracle(a,b))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Canonical parts class/sign/exponent/fraction ordering checked, including NaN, infinities and signed zero; unpacking integration and hardware timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-fpcmp-parts-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
