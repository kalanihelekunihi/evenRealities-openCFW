# SPDX-License-Identifier: MIT
"""Host upstream packer check against independent integer rounding oracle."""
import ctypes,json,subprocess,random
from build_gx8002_pack_double import build,ROOT

def rounded(n,shift):
    if shift<=0:return n<<(-shift)
    q,r=divmod(n,1<<shift);half=1<<(shift-1)
    return q+int(r>half or (r==half and q&1))
def oracle(c,s,e,f):
    sign=s<<63
    if c<2:return sign|(2047<<52)|(1<<51)|((f>>8)&((1<<51)-1))
    if c==4:return sign|(2047<<52)
    if c==2 or not f:return sign
    if e>1023:return sign|(2047<<52)
    if e<-1022:
        n=rounded(f,-e-1014)
        return sign|n
    n=rounded(f,8)
    if n>=1<<53:n>>=1;e+=1
    return sign|((e+1023)<<52)|(n&((1<<52)-1))
def verify():
    candidate=build();out=ROOT/'build/gx8002-pack_double';source=(out/'candidate.c').read_text().replace('} fp_number_type;','} __attribute__((packed, aligned(4))) fp_number_type;')
    source+='\nuint64_t checked_pack(unsigned c,unsigned s,int e,uint64_t f) { fp_number_type p={c,s,e,{f}}; FLO_union_type u; u.value=pack_d(&p); return u.value_raw; }\n'
    p=out/'host.c';p.write_text(source);lib=out/'host.dylib';subprocess.run(['clang','-O2','-shared','-fPIC',str(p),'-o',str(lib)],check=True)
    fn=ctypes.CDLL(str(lib)).checked_pack;fn.argtypes=[ctypes.c_uint,ctypes.c_uint,ctypes.c_int,ctypes.c_uint64];fn.restype=ctypes.c_uint64
    values=[(c,s,e,f) for c in range(5) for s in (0,1) for e in (-1100,-1075,-1074,-1023,-1022,0,1023,1024) for f in (1<<60,(1<<60)+128,(1<<60)+384,(1<<61)-1)]
    rng=random.Random(738);values.extend((3,rng.randrange(2),rng.randrange(-1100,1025),rng.randrange(1<<60,1<<61)) for _ in range(2000))
    for c,s,e,f in values:assert fn(c,s,e,f)==oracle(c,s,e,f),(c,s,e,hex(f),hex(fn(c,s,e,f)),hex(oracle(c,s,e,f)))
    return {'candidate':candidate,'host_cases':len(values),'source_admitted':False,'limits':['Host macOS C rounding oracle only; target decoding, ABI and size fit outstanding.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-pack-double-host.json').write_text(json.dumps(r,indent=2)+'\n');print(r['host_cases'])
