# SPDX-License-Identifier: MIT
"""Execute binary64 scalbn against exact dyadic nearest-even rounding."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute


def reference(value,n):
    sign=value&(1<<63);exponent=(value>>52)&2047
    mant=(value&((1<<52)-1))|((1<<52) if exponent else 0)
    if not mant:return sign
    power=(exponent-1075 if exponent else -1074)+n
    top=mant.bit_length()-1+power
    if top>1023:return sign|0x7ff0000000000000
    if top < -1075:return sign
    quantum=max(-1074,top-52);shift=quantum-power
    if shift>0:
        q,remainder=divmod(mant,1<<shift);half=1<<(shift-1)
        q+=remainder>half or (remainder==half and q&1)
    else:q=mant<<-shift
    if not q:return sign
    top=q.bit_length()-1+quantum
    if top>1023:return sign|0x7ff0000000000000
    if top < -1022:return sign|q
    if q.bit_length()>53:q>>=1
    return sign|((top+1023)<<52)|(q&((1<<52)-1))


def verify():
    path=ROOT/'build/gx8002-reduction-source-closure/reduction.elf';report=json.loads((ROOT/'docs/research/gx8002-reduction-source-closure.json').read_text())
    assert sha(path.read_bytes())==report['elf_sha256'];elf=Elf32(path.read_bytes(),'reduction')
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
    memory={s['address']+i:b for s in elf.sections if s['flags']&2 and s['size'] and s['type']!=8 for i,b in enumerate(elf.contents(s))}
    entry=next(s['value'] for s in elf.symbols() if s['name']=='scalbn')
    edges=[(s<<63)|(e<<52)|f for s in (0,1) for e in (0,1,2,1022,1023,1024,2045,2046) for f in (0,1,2,1<<51,(1<<52)-1)]
    shifts=[-2147483648,-50001,-2098,-1075,-1074,-1024,-54,-53,-1,0,1,53,54,1023,1024,2098,50001,2147483647]
    pairs=[(x,n) for x in edges for n in shifts]
    rng=random.Random(80464);pairs += [(rng.getrandbits(64),rng.randrange(-2100,2101)) for _ in range(2000)]
    errors=[];count=0
    for value,n in pairs:
        if (value>>52)&2047==2047:continue
        expected=reference(value,n)
        actual=execute(code,entry,bytes(20),arguments=[value&0xffffffff,value>>32,n&0xffffffff],return_pair=True,readonly=memory,max_steps=10000)
        if actual!=expected:errors.append({'value':hex(value),'shift':n,'actual':hex(actual),'expected':hex(expected)})
        count+=1
    result={'source_elf_sha256':report['elf_sha256'],'finite_cases':count,'errors':errors,'source_admitted':False,'limits':['Exact integer dyadic reference with nearest-even rounding. Exercises signed zeros, subnormals, overflow, underflow and extreme int shifts. Reports discrepancies without accepting them. Nonfinite values, complete reducer execution, placement and hardware pending.']}
    (ROOT/'docs/research/gx8002-reduction-scalbn.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=verify();print(r['finite_cases'],len(r['errors']),r['errors'][:3])
