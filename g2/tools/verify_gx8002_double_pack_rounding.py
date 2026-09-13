# SPDX-License-Identifier: MIT
"""Validate decoded source pack rounding against exact integer quantization."""
import json,struct,subprocess,random
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def rounded_shift(n,shift):
    if shift<=0:return n<<(-shift)
    q,r=divmod(n,1<<shift);half=1<<(shift-1)
    return q+int(r>half or (r==half and q&1))

def oracle(sign,exponent,fraction):
    # Exact magnitude is fraction * 2**(exponent-60).
    if not fraction:return sign<<63
    top=fraction.bit_length()-1;power=exponent-60+top
    if power < -1022:
        bits=rounded_shift(fraction,-(exponent-60+1074))
        assert bits<=1<<52
    else:
        sig=rounded_shift(fraction,top-52)
        if sig==1<<53:sig>>=1;power+=1
        bits=0x7ff0000000000000 if power>1023 else ((power+1023)<<52)|(sig- (1<<52))
    return (sign<<63)|bits

def verify():
    path=ROOT/'build/gx8002-double-core-layout/core.elf';report=json.loads((ROOT/'docs/research/gx8002-double-core-layout.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    e=Elf32(path.read_bytes(),'core');entry=next(s['value'] for s in e.symbols() if s['name']=='__pack_d')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    exponents=[-1200,*range(-1080,-1019),-1,0,1,1022,1023,1024]
    # Normalized internal significand, with all guard-byte residues and both tie parities.
    fractions=[(base<<8)|residue for base in ((1<<52),(1<<52)+1,(1<<53)-2,(1<<53)-1) for residue in range(256)]
    cases=0;failures=[]
    for exponent in exponents:
        for fraction in fractions:
            for sign in (0,1):
                parts=struct.pack('<5I',3,sign,exponent&0xffffffff,fraction&0xffffffff,fraction>>32)
                actual=execute(code,entry,parts);expected=oracle(sign,exponent,fraction)
                if actual!=expected:failures.append({'sign':sign,'exponent':exponent,'fraction':hex(fraction),'actual':hex(actual),'expected':hex(expected)})
                cases+=1
    result={'source_elf_sha256':sha(path.read_bytes()),'cases':cases,'failure_count':len(failures),'failures':failures[:20],'source_admitted':False,'limits':['Exact integer round-to-nearest-even oracle on normalized internal significands; every 8-bit residue at selected exponent/significand boundaries. Stock pack and arbitrary noncanonical parts remain unqualified.']}
    (ROOT/'docs/research/gx8002-double-pack-rounding.json').write_text(json.dumps(result,indent=2)+'\n');assert not failures,result
    return result
if __name__=='__main__':print(verify())
