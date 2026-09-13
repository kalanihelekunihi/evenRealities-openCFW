# SPDX-License-Identifier: MIT
"""Check corrected source binary64 special values, including zero divisors."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

MASK=(1<<63)-1
INF=0x7ff0000000000000
QNAN=0x7ff8000000000000

def oracle(name,a,b):
    sign=(a^b)&(1<<63);x,y=a&MASK,b&MASK
    nan=a if x>INF else b if y>INF else None
    if nan is not None:
        value=nan|(1<<51)
        return (value&MASK)|sign if name=='mul' else value
    if name=='mul':
        if (x==INF and y==0) or (y==INF and x==0):return QNAN
        if x==INF or y==INF:return sign|INF
        assert x==0 or y==0
        return sign
    if (x==INF and y==INF) or (x==0 and y==0):return QNAN
    if x==INF or y==0:return sign|INF
    assert x==0 or y==INF
    return sign

def verify():
    path=ROOT/'build/gx8002-double-muldiv-corrected/muldiv.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-double-muldiv-corrected.json').read_text());assert sha(data)==report['elf_sha256']
    elf=Elf32(data,'corrected');symbols={s['name']:s['value'] for s in elf.symbols()}
    nan=next(s for s in elf.sections if s['name']=='.nan');constant=elf.contents(nan)
    assert constant==bytes(20) and symbols['__thenan_df']==nan['address']
    readonly={nan['address']+i:b for i,b in enumerate(constant)}
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
    rng=random.Random(804);payloads=[0,1,(1<<52)-1]+[1<<n for n in range(52)]+[rng.getrandbits(52) for _ in range(128)]
    special=[(s<<63)|INF|p for s in (0,1) for p in payloads]+[0,1<<63]
    other=[0,1,1<<63,0x3ff0000000000000,0xbff0000000000000,0x7fefffffffffffff,INF,INF|(1<<63),QNAN|123,0xfff0000000000123]
    pairs=[(a,b) for a in special for b in other]+[(b,a) for a in special for b in other]
    for name in ('mul','div'):
        for a,b in pairs:
            actual=execute(code,symbols['__'+name+'df3'],bytes(20),arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32],return_pair=True,readonly=readonly)
            expected=oracle(name,a,b)
            assert actual==expected,(name,hex(a),hex(b),hex(actual),hex(expected))
    result={'source_elf_sha256':sha(data),'cases':len(pairs)*2,'source_admitted':False,'limits':['Actual corrected source, pack/unpack and typed NaN data execution. NaN sign conventions follow upstream source and remain to be compared with stock. Exception flags, references, integration and hardware are not qualified.']}
    (ROOT/'docs/research/gx8002-double-muldiv-nonfinite.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
