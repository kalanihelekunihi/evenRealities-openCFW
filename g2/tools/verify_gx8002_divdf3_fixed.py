# SPDX-License-Identifier: MIT
"""Broad decoded division including exceptional binary64 bit patterns."""
import json,subprocess,struct,math,random
from itertools import product
from analyze_gx8002_upstream_objects import ROOT,sha,IMAGE_SHA
from build_transparent_image import Elf32
from execute_gx8002_muldf3 import execute
from verify_gx8002_memcpy_source import decode

def integer_quotient_bits(a,b):
    """Exact finite binary64 quotient, rounded once to nearest/even."""
    sign=(a^b)&(1<<63)
    def parts(v):
        exponent=(v>>52)&2047;fraction=v&((1<<52)-1)
        assert exponent != 2047
        return ((1<<52)|fraction,exponent-1075) if exponent else (fraction,-1074)
    av,ae=parts(a);bv,be=parts(b);e=ae-be
    assert bv
    if not av:return sign
    k=av.bit_length()-bv.bit_length()
    if (av < (bv<<k)) if k>=0 else ((av<<(-k)) < bv):k-=1
    exponent=k+e
    shift=e-max(exponent,-1022)+52
    n,d=(av<<shift,bv) if shift>=0 else (av,bv<<(-shift))
    sig,rem=divmod(n,d);sig+=int(2*rem>d or (2*rem==d and sig&1))
    if exponent < -1022:return sign|sig
    if sig >= 1<<53:sig>>=1;exponent+=1
    if exponent>1023:return sign|0x7ff0000000000000
    return sign|((exponent+1023)<<52)|(sig&((1<<52)-1))

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x13894','--stop-address=0x13d74',str(p)],text=True));new={};evidence={}
    for name in ('divdf3-fixed','unpack_double','pack_double'):
        p=ROOT/('build/gx8002-'+name+'/candidate.elf');e=Elf32(p.read_bytes(),name);r=json.loads((ROOT/('docs/research/gx8002-'+name+'-candidate.json')).read_text());assert sha(e.contents(next(s for s in e.sections if s['name']=='.text')))==r['compiled_sha256'];evidence[name]=sha(p.read_bytes());new.update(decode(subprocess.check_output([pre,'-d',str(p)],text=True)))
    edges=[0,1,0x000fffffffffffff,0x0010000000000000,0x3fefffffffffffff,0x3ff0000000000000,0x3ff0000000000001,0x7fefffffffffffff,0x7ff0000000000000,0x7ff0000000000001,0x7ff8000000001234];edges += [x|(1<<63) for x in edges];values=list(product(edges,edges));rng=random.Random(548);values.extend((rng.getrandbits(64),rng.getrandbits(64)) for _ in range(4000));numeric=0;discrepancies=[];corrections=[]
    # Quotient exponent sweeps all underflow shifts and the normal boundary.
    boundary=[]
    for shift in range(58):
        for _ in range(32):
            ea=rng.randrange(1,900);eb=ea+1022+shift
            if eb > 2046:continue
            a=(ea<<52)|rng.getrandbits(52);b=(eb<<52)|rng.getrandbits(52)
            boundary.extend(((a,b),(a|(1<<63),b)))
    values.extend(boundary)
    for a,b in values:
        results=[execute(code,entry,a,b,up,pk,mul,raw=True) for code,entry,up,pk,mul in ((old,0x13894,0x13c90,0x13b00,0x13ab4),(new,0x1020a308,0x1020a704,0x1020a574,0x1020a528))]
        if results[0]!=results[1]:corrections.append({'left':hex(a),'right':hex(b),'stock':hex(results[0]),'fixed':hex(results[1])})
        x,y=[struct.unpack('<d',struct.pack('<Q',v))[0] for v in (a,b)];value=(math.nan if x==0 or math.isnan(x) else math.copysign(math.inf,x)*math.copysign(1.0,y)) if y==0 else x/y
        if not math.isnan(value):
            expected=struct.unpack('<Q',struct.pack('<d',value))[0]
            assert results[1]==expected,(hex(a),hex(b),hex(results[1]),hex(expected))
            if ((a>>52)&2047)!=2047 and ((b>>52)&2047)!=2047 and (b&((1<<63)-1)):
                assert results[1]==integer_quotient_bits(a,b),('integer oracle',hex(a),hex(b))
            numeric+=1
        else:assert results[0]==results[1],('NaN changed',hex(a),hex(b),results)
    return {'corrections':corrections,'cases':len(values),'numeric_cases':numeric,'targeted_underflow_cases':len(boundary),'ieee_discrepancies':discrepancies,'elf_sha256':evidence,'limits':['Decoded divide/unpack/pack integration and ABI; exact exceptional payload comparison to stock and explicit discrepancies against non-NaN IEEE host oracle. Physical timing/exception flags unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-divdf3-fixed-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
