# SPDX-License-Identifier: MIT
"""Execute source multiply/divide against exact rational finite arithmetic."""
import json,random,math,subprocess
from fractions import Fraction
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_double_addsub_target import floating,bits

def verify(operations=("mul","div"),corrected=False):
    stem='gx8002-double-muldiv-corrected' if corrected else 'gx8002-double-muldiv-cluster'
    path=ROOT/'build'/stem/'muldiv.elf'
    report=json.loads((ROOT/'docs/research'/(stem+'.json')).read_text());assert sha(path.read_bytes())==report['elf_sha256']
    elf=Elf32(path.read_bytes(),'muldiv');symbols={s['name']:s['value'] for s in elf.symbols()}
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    edge=[(s<<63)|(e<<52)|f for s in (0,1) for e in (0,1,2,1022,1023,1024,2045,2046) for f in (0,1,1<<51,(1<<52)-1)]
    pairs=[(a,b) for a in edge for b in edge];rng=random.Random(804)
    pairs += [(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(10000)]
    pairs=[(a,b) for a,b in pairs if (a>>52)&2047!=2047 and (b>>52)&2047!=2047]
    counts={}
    for name in operations:
        assert name in ('mul','div')
        count=0
        for a,b in pairs:
            if name=='div' and b&((1<<63)-1)==0:continue
            x,y=Fraction(floating(a)),Fraction(floating(b));exact=x*y if name=='mul' else x/y
            sign=(a^b)&(1<<63)
            try:expected=bits(float(exact)) if exact else sign
            except OverflowError:expected=sign|0x7ff0000000000000
            actual=execute(code,symbols['__'+name+'df3'],bytes(20),arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32],return_pair=True)
            assert actual==expected,(name,hex(a),hex(b),hex(actual),hex(expected))
            count+=1
        counts[name]=count
    result={'source_elf_sha256':sha(path.read_bytes()),'finite_cases':counts,'source_admitted':False,'limits':['Actual decoded source arithmetic and pack/unpack dependencies versus exact rational rounding. Nonfinite behavior, stock comparison, references, integration and hardware remain pending.']}
    (ROOT/'docs/research'/('gx8002-double-'+'-'.join(operations)+('-corrected' if corrected else '')+'-target.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
